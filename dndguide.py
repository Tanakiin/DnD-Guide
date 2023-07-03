
import PySimpleGUI as sg
import requests
import time as t
import textwrap as tw


GRAPH_SIZE = (300 , 300)
CIRCLE_LINE_WIDTH, LINE_COLOR = 20, 'yellow'
TEXT_FONT = 'Courier'

TEXT_HEIGHT = GRAPH_SIZE[0]//4
TEXT_LOCATION = (GRAPH_SIZE[0]//2, GRAPH_SIZE[1]//2)
TEXT_COLOR = LINE_COLOR

def update_meter(graph_elem, percent_complete):
    """
    Update a circular progress meter
    :param graph_elem:              The Graph element being drawn in
    :type graph_elem:               sg.Graph
    :param percent_complete:        Percentage to show complete from 0 to 100
    :type percent_complete:         float | int
    """
    graph_elem.erase()
    arc_length = percent_complete/100*360+.9
    if arc_length >= 360:
        arc_length = 359.9
    graph_elem.draw_arc((CIRCLE_LINE_WIDTH, GRAPH_SIZE[1] - CIRCLE_LINE_WIDTH), (GRAPH_SIZE[0] - CIRCLE_LINE_WIDTH, CIRCLE_LINE_WIDTH),
                   arc_length, 0, 'arc', arc_color=LINE_COLOR, line_width=CIRCLE_LINE_WIDTH)
    percent = percent_complete
    graph_elem.draw_text(f'{percent:.0f}%', TEXT_LOCATION, font=(TEXT_FONT, -TEXT_HEIGHT), color=TEXT_COLOR)


def dupe(old):
    seen = {}
    for x in old:
        if x in seen:
            seen[x] += 1
            yield "%s(%d)" % (x, seen[x])
        else:
            seen[x] = 0
            yield x

def text(txt, size, fx=''):
        if txt == '':
            return sg.Text('N/A', size=(3, 1), font=("Bahnschrift", size, fx))
        else:
            return sg.Text(str(txt).capitalize(), size=(len(str(txt))+1, 1), font=("Bahnschrift", size, fx))

def ctext(txt, size, fx=''):
        if txt == '':
            txt = 'N/A'
        return sg.Text(str(txt), size=(len(str(txt))+1, 1), font=("Bahnschrift", size, fx))

def status(txt, size):
    return sg.StatusBar(txt, font=("Bahnschrift", size))

def frame(txt, size):
    return sg.Frame('', [[text(txt, size)]], element_justification='center')

def frames(txt, w):
    wrap = tw.TextWrapper(width=w)
    return sg.Frame('', [[sg.Text(wrap.fill(txt), font=("Bahnschrift", 12))]])

def mult(txt, size):
    return sg.Multiline(str(txt), font=("Bahnschrift", size),expand_y=True, expand_x=True, size=(23, 10))

def s_monster(mon):
    response = requests.get(f"https://api.open5e.com/monsters/?search={mon}")
    data = response.json()
    n = [i['name'] for i in data['results']]
    s = [i['slug'] for i in data['results']]
    n = list(dupe(n))
    results = {n[i]: s[i] for i in range(len(n))}
    names = list(results.keys())
    num = data['count']
    print(results)
    return results, names, num

def monster(mon):
    response = requests.get(f"https://api.open5e.com/monsters/{mon}")
    data = response.json()
    return(data)

def multiresult(names, num):
    layout = [[sg.Titlebar('Search Results', font=("Bahnschrift", 12), background_color="#1c1e23")],
              [sg.Text(f'{num} Search Results', size=(14, 1), font='Bahnschrift '+ str(15))],
              [sg.Combo(names, default_value=names[0],key='results', font='Bahnschrift '+str(12))],
              [sg.Button('Select', font='Bahnschrift '+str(10), key='select')],
              [sg.ProgressBar(50, orientation='h', size=(18, 20),key='pbar2', bar_color=("#8b9fde", "#2e3d5a"))]]
    return layout

def statcol(d):
    col1 = [[ctext('Strength:',12), sg.Push(), frame(d['strength'],12)],
            [ctext('Dexterity:',12),sg.Push(),  frame(d['dexterity'], 12)],
            [ctext('Constitution:', 12), sg.Push(), frame(d['constitution'], 12)]]
    col2 = [[ctext('Intelligence:',12), sg.Push(), frame(d['intelligence'],12)],
            [ctext('Wisdom:', 12), sg.Push(), frame(d['wisdom'],12)],
            [ctext('Charisma:',12), sg.Push(), frame(d['charisma'],12)]]
    col3 = [[text('Speed', 14, 'bold')]]
    for i in d['speed']:
        col3.append([text(i,12), frame(d['speed'][i], 12)])
    col4 = [[ctext('Strength Save:',12), sg.Push(),frame(d['strength_save'],12)],
            [ctext('Dexterity Save:',12), sg.Push(),frame(d['dexterity_save'], 12)],
            [ctext('Constitution Save:', 12), sg.Push(),frame(d['constitution_save'], 12)]]
    col5 = [[ctext('Intelligence Save:',12),sg.Push(), frame(d['intelligence_save'],12)],
            [ctext('Wisdom Save:', 12), sg.Push(),frame(d['wisdom_save'],12)],
            [ctext('Charisma Save:',12), sg.Push(),frame(d['charisma_save'],12)]]
    return [col1, col2, col3, col4, col5]

def aff(d):
    return [[ctext('Damage Vulnerabilities:', 12), sg.Push(), frame(d['damage_vulnerabilities'], 12)],
            [ctext('Damage Resistances:', 12), sg.Push(), frame(d['damage_resistances'], 12)],
            [ctext('Damage Immunities:', 12), sg.Push(), frame(d['damage_immunities'], 12)],
            [ctext('Condition Immunities:', 12), sg.Push(), frame(d['condition_immunities'], 12)],
            [text('Senses:', 12),sg.Push(),  frame(d['senses'], 12)],
            [text('Languages:',12), sg.Push(), frame(d['languages'],12)]]

def acc(d):
    out = []
    for i in d['actions']:
        tmp = [[text('Name', 12), frame(i['name'], 12)],
               [text('Description', 12)],
               [frames(i['desc'], 21)]]
        out.append(sg.vtop(sg.Column(tmp, scrollable=True, vertical_scroll_only=True, size=(200, 230), size_subsample_height=1, expand_y=True)))
    return out

def legg(d):
    out = []
    for i in d['legendary_actions']:
        tmp = [[text('Name', 12), frame(i['name'], 12)],
               [text('Description', 12)],
               [frames(i['desc'], 21)]]
        out.append(sg.vtop(sg.Column(tmp, scrollable=True, vertical_scroll_only=True, size=(200, 230), size_subsample_height=1, expand_y=True)))
    return out

def spec(d):
    out = []
    for i in d['special_abilities']:
        tmp = [[text('Name', 12), frame(i['name'], 12)],
               [text('Description', 12)],
               [frames(i['desc'], 21)]]
        out.append(sg.vtop(sg.Column(tmp, scrollable=True, vertical_scroll_only=True, size=(200, 230), size_subsample_height=1, expand_y=True)))
    return out

def spel_dict(ls):
    d = {}
    for i in ls:
        x = (i.split("/")[-2]).split("-")
        x = " ".join([i.capitalize() for i in x])
        d[x] = i
    return d

def mult_spel(d):
    dic = spel_dict(d['spell_list'])
    return [[sg.VPush()],
            [sg.Column([[sg.Listbox(list(dic.keys()), default_values=list(dic.keys())[0], key='s_results', font=("Bahnschrift", 20), size=(40, 4), ), sg.Button('Search Spell', font=("Bahnschrift", 12), key='s_select', size=(15, 4))]]), sg.Push() ,sg.ProgressBar(50, orientation='v', size=(18, 20),key='pbar3', bar_color=("#8b9fde", "#2e3d5a"))],
            [sg.VPush()]], dic

def f_monster(mon):
    is_leg=True
    is_spec=True
    is_spel=True
    d = monster(mon)
    co = statcol(d)
    co2 = aff(d)
    co3 = acc(d)
    co4 = legg(d)
    co5 = spec(d)
    co6 = []
    dic = {}
    if d['legendary_desc']=="":
        is_leg = False
    if len(d['special_abilities'])==0:
        is_spec = False
    if len(d['spell_list']) == 0:
        is_spel = False
    else:
        co6, dic = mult_spel(d)
    layout = [[sg.Titlebar(d['name'], font=("Bahnschrift", 12), background_color="#1c1e23")],
              [text(d['name'], 25,'bold')],
              [sg.HSep()],
              [ctext('General Info', 14, 'bold')],
              [text('Size:',12), frame(d['size'],12), text("Type:",12), frame(d['type'].capitalize(),12),text("Subtype:",12), frame(d['subtype'].capitalize(),12), text("Alignment:",12), frame(d['alignment'].capitalize(),12), ctext("Challenge Rating", 12), frame(d['cr'],12), sg.Push()],
              [sg.HSep()],
              [ctext("Armour and Hit Points", 14, 'bold')],
              [ctext('Armour Class:',12), frame(d['armor_class'],12), ctext('Armour Description:', 12), frame(d['armor_desc'],12), ctext('Hit Points:',12), frame(d['hit_points'], 12), ctext('Hit Dice:', 12), frame(d['hit_dice'], 12), sg.Push()],
              [sg.HSep()],
              [sg.Push(), text('Stats',14, 'bold'), sg.Push(), sg.Push(), text('Saves',14, 'bold'), sg.Push()],
              [sg.Column(co[0]), sg.Column(co[1]), sg.Column(co[2]), sg.VSep(), sg.Column(co[3]), sg.Column(co[4])],
              [sg.HSep()],
              [sg.TabGroup([[sg.Tab('Affinities', [[sg.Column(co2)]]), sg.Tab('Actions', [co3]), sg.Tab('Legendary Actions', [co4], visible=is_leg), sg.Tab('Special Abilities', [co5], visible=is_spec), sg.Tab('Spells', co6, visible=is_spel)]], font=("Bahnschrift", 12))],
              ]
    # 
    return sg.Window(d['name'], layout), dic

##############################################################

def s_spell(spl):
    response = requests.get(f"https://api.open5e.com/spells/?search={spl}")
    data = response.json()
    n = [i['name'] for i in data['results']]
    s = [i['slug'] for i in data['results']]
    n = list(dupe(n))
    results = {n[i]: s[i] for i in range(len(n))}
    names = list(results.keys())
    num = data['count']
    print(results)
    return results, names, num

def spell(spl):
    response = requests.get(f"https://api.open5e.com/spells/{spl}")
    data = response.json()
    return(data)

def deps(d):
    return [[sg.Push(), text('Dependencies',14, 'bold'), sg.Push()],
            [ctext('Cast as Ritual:',12), sg.Push(), frame(d['can_be_cast_as_ritual'],12)],
            [ctext('Needs Concentration:',12), sg.Push(), frame(d['requires_concentration'],12)],
            [ctext('Verbal Component:',12), sg.Push(), frame(d['requires_verbal_components'],12)],
            [ctext('Somatic Component:',12), sg.Push(), frame(d['requires_somatic_components'],12)],
            [ctext('Material Component:',12), sg.Push(), frame(d['requires_material_components'],12)],]

def g_info(d):
    return [[sg.Push(), ctext('General Info', 14, 'bold'), sg.Push()],
            [text('Duration:', 12), sg.Push(), frame(d['duration'], 12)],
            [text('Materials:', 12), sg.Push(), frame(d['material'], 12)],
            [text('Range:', 12), sg.Push(), frame(d['range'], 12)],
            [text('Casting Time:', 12), sg.Push(), frame(d['casting_time'], 12)],
            [text('Level:', 12), sg.Push(), frame(d['level'], 12)]]

def f_spell(spl="", d=""):
    if d=="":
        d = spell(spl)
    hl = True
    if d['higher_level']=="":
        hl = False
    co = deps(d)
    co2 = [[sg.Column([[frames(d['desc'], 90)]], scrollable=True,vertical_scroll_only=True, size=(750, 200), expand_x=True)]]  
    co3 = [[sg.Column([[frames(d['higher_level'], 90)]], scrollable=True,vertical_scroll_only=True, size=(700, 100), expand_x=True)]]
    co4 = g_info(d)
    layout = [[sg.Titlebar(d['name'], font=("Bahnschrift", 12), background_color="#1c1e23")],
              [text(d['name'], 25,'bold'), sg.Push(), frame(d['school'], 13)],
              [sg.HSep()],
              [sg.TabGroup([[sg.Tab('Description', co2), sg.Tab('Higher Level', co3, visible=hl)]], font=("Bahnschrift", 12))],
              [sg.HSep()],
              [sg.Column(co), sg.VSep(), sg.Column(co4)],
              [sg.HSep()],
              [text('Circles:', 12), sg.Push(), frame(d['circles'], 12)],
              [ctext('Usable Classes:', 12), sg.Push(), frame(d['dnd_class'], 12)]
              ]
    return sg.Window(d['name'], layout)

##############################################################

def s_item(itm):
    response = requests.get(f"https://api.open5e.com/magicitems/?search={itm}")
    data = response.json()
    n = [i['name'] for i in data['results']]
    s = [i['slug'] for i in data['results']]
    n = list(dupe(n))
    results = {n[i]: s[i] for i in range(len(n))}
    names = list(results.keys())
    num = data['count']
    print(results)
    return results, names, num

def item(itm):
    response = requests.get(f"https://api.open5e.com/magicitems/{itm}")
    data = response.json()
    return(data)

def f_item(itm):
    d = item(itm)
    x = ""
    if d['requires_attunement'] == "":
        x == "False"
    layout = [[sg.Titlebar(d['name'], font=("Bahnschrift", 12), background_color="#1c1e23")],
              [text(d['name'],25, 'bold')],
              [sg.HSep()],
              [ctext('General Info', 14, 'bold')],
              [text('Description:', 12), frames(d['desc'], 60)],
              [text('Type:', 12), sg.Push(), frame(d['type'], 12)],
              [text('Rarity:', 12), sg.Push(), frame(d['rarity'], 12)],
              [text("Attunement: ", 12), sg.Push(), frame(x, 12)]]
    return sg.Window(d['name'], layout)

##############################################################

def s_wps(wp):
    response = requests.get(f"https://api.open5e.com/weapons/?search={wp}")
    data = response.json()
    n = [i['name'] for i in data['results']]
    s = [i['slug'] for i in data['results']]
    n = list(dupe(n))
    results = {n[i]: s[i] for i in range(len(n))}
    names = list(results.keys())
    num = data['count']
    print(results)
    return results, names, num

def wps(wp):
    response = requests.get(f"https://api.open5e.com/weapons/{wp}")
    data = response.json()
    return(data)

def f_wps(wp):
    d = wps(wp)
    print(d)
    co = []
    for i in d['properties']:
        co.append([sg.Push(), frame(i, 12)])
    layout = [[sg.Titlebar(d['name'], font=("Bahnschrift", 12), background_color="#1c1e23")],
              [text(d['name'],25, 'bold')],
              [sg.HSep()],
              [ctext('General Info', 14, 'bold')],
              [text('Category:', 12), frame(d['category'], 12)],
              [text('Cost:', 12), sg.Push(), frame(d['cost'], 12)],
              [text('Damage Dice:', 12), sg.Push(), frame(d['damage_dice'], 12)],
              [text("Damage Type: ", 12), sg.Push(), frame(d['damage_type'], 12)],
              [text('Weight:', 12), sg.Push(), frame(d['weight'], 12)],
              [sg.HSep()],
              [text('Properties:', 12), sg.Push(), sg.Column(co)]]
    return sg.Window(d['name'], layout)

sg.theme('Dark Grey 12')

PIN = '📌'
EXIT = '❌'

my_titlebar = [[sg.Text('DnD Guide', expand_x=True, grab=True, font=("Bahnschrift", 15), pad=(0,0)),
                    sg.Push(), sg.Button(EXIT, font=("Bahnschrift", 12), key='exit'),
                    sg.Text(PIN, enable_events=True, k='-PIN-',  font='_ 12', pad=(0,0),  metadata=False,
                            text_color=sg.theme_background_color(), background_color=sg.theme_text_color())]]



layout = [[sg.Titlebar('DnD Guide', font=("Bahnschrift", 12), background_color="#1c1e23")],
          [sg.Input(size=(55,5), font='Bahnschrift '+str(12), key='search')],
          [sg.Button('Search Monster',font=("Bahnschrift", 10), key='mon'), sg.Button('Search Spell',font="Bahnschrift "+str(10), key='spl'), sg.Button('Search Item',font="Bahnschrift "+str(10), key='itm'), sg.Button('Search Weapon',font="Bahnschrift "+str(10), key='wp')],
          [sg.ProgressBar(50, orientation='h', size=(38.2, 20),key='pbar', bar_color=("#8b9fde", "#2e3d5a"))]]

window = sg.Window("DnD Guide", layout, element_justification='l', resizable=True)

def do_mon(event, values):
    s_mon = values['search'].lower().replace(' ', '%20')
    results, names, num = s_monster(s_mon)
    for i in range(0, num):
        e,v = window.read(10)
        window['pbar'].update(max=num, current_count=i+1)
    t.sleep(0.25)
    if int(num) >= 1:
        layout2 = multiresult(names, num)
        popup = sg.Window("Search", layout2)
        while True:
            ev2, val2 = popup.read()
            print(ev2, val2)
            if ev2 == sg.WIN_CLOSED:
                break
            for i in range(0, num):
                e1,v1 = window.read(10)
                popup['pbar2'].update(max=num, current_count=i+1)
            if ev2 == 'select':
                mon = results[val2['results']]
                popup1, dic = f_monster(mon)
                while True:
                    e2, v2 = popup1.read()
                    if e2 == sg.WIN_CLOSED:
                        break
                    for i in range(0, 20):
                        e1,v1 = window.read(10)
                        popup1['pbar3'].update(max=num, current_count=i+1)
                    if e2 == 's_select':
                        print(e2,v2)
                        response = requests.get(dic[v2['s_results'][0]])
                        dt = response.json()
                        popup2 = f_spell(d=dt)
                        while True:
                            e2, v2 = popup2.read()
                            if e2 == sg.WIN_CLOSED:
                                break
    else:
            sg.popup("Search has no results!", font=("Bahnschrift",12))

def do_spell(event, values):
    s_spl = values['search'].lower().replace(' ', '%20')
    results, names, num = s_spell(s_spl)
    for i in range(0, num):
        e,v = window.read(10)
        window['pbar'].update(max=num, current_count=i+1)
    t.sleep(0.25)
    if int(num) >= 1:
        layout2 = multiresult(names, num)
        popup = sg.Window("Search", layout2)
        while True:
            ev2, val2 = popup.read()
            print(ev2, val2)
            if ev2 == sg.WIN_CLOSED:
                break
            for i in range(0, 20):
                e1,v1 = window.read(10)
                popup['pbar2'].update(max=num, current_count=i+1)
            if ev2 == 'select':
                sp = results[val2['results']]
                popup1 = f_spell(sp)
                while True:
                    e2, v2 = popup1.read()
                    if e2 == sg.WIN_CLOSED:
                        break
                    
    else:
            sg.popup("Search has no results!", font=("Bahnschrift",12))

def do_item(event, values):
    s_itm = values['search'].lower().replace(' ', '%20')
    results, names, num = s_item(s_itm)
    print(names)
    for i in range(0, num):
        e,v = window.read(10)
        window['pbar'].update(max=num, current_count=i+1)
    t.sleep(0.25)
    if int(num) >= 1:
        layout2 = multiresult(names, num)
        popup = sg.Window("Search", layout2)
        while True:
            ev2, val2 = popup.read()
            print(ev2, val2)
            if ev2 == sg.WIN_CLOSED:
                break
            for i in range(0, 20):
                e1,v1 = window.read(10)
                popup['pbar2'].update(max=num, current_count=i+1)
            if ev2 == 'select':
                sp = results[val2['results']]
                popup1 = f_item(sp)
                while True:
                    e2, v2 = popup1.read()
                    if e2 == sg.WIN_CLOSED:
                        break
    else:
            sg.popup("Search has no results!", font=("Bahnschrift",12))

def do_wp(event, values):
    s_wp = values['search'].lower().replace(' ', '%20')
    results, names, num = s_wps(s_wp)
    for i in range(0, num):
        e,v = window.read(10)
        window['pbar'].update(max=num, current_count=i+1)
    t.sleep(0.25)
    if int(num) >= 1:
        layout2 = multiresult(names, num)
        popup = sg.Window("Search", layout2)
        while True:
            ev2, val2 = popup.read()
            print(ev2, val2)
            if ev2 == sg.WIN_CLOSED:
                break
            for i in range(0, 20):
                e1,v1 = window.read(10)
                popup['pbar2'].update(max=num, current_count=i+1)
            if ev2 == 'select':
                wp = results[val2['results']]
                print(wp)
                popup1 = f_wps(wp)
                while True:
                    e2, v2 = popup1.read()
                    if e2 == sg.WIN_CLOSED:
                        break
    else:
            sg.popup("Search has no results!", font=("Bahnschrift",12))

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'exit':
        break
    if event == 'mon':
        do_mon(event, values)
    if event == 'spl':
        do_spell(event, values)
    if event == 'itm':
        do_item(event, values)
    if event == 'wp':
        do_wp(event, values)
    if event == '-PIN-':
            window['-PIN-'].metadata = not window['-PIN-'].metadata
            if window['-PIN-'].metadata:
                window['-PIN-'].update(text_color='red')
                window.keep_on_top_set()
            else:
                window['-PIN-'].update(text_color=sg.theme_background_color())
                window.keep_on_top_clear()
window.close()

