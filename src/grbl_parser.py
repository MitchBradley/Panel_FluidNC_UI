class GrblParser:
    def __init__(self, callback):
        self.callback = callback
        self.WCO = None
        self.OVR = {'feed': None, 'rapid': None, 'spindle': None}
        self.OVRchanged = False
        self.MPOS = [0, 0, 0, 0]
        self.WPOS = [0, 0, 0, 0]
        self.axisNames = ['x', 'y', 'z', 'a', 'b', 'c']
        self.modal = {'modes': '', 'plane': 'G17', 'units': 'G21', 'wcs': 'G54', 'distance': 'G90'}
        self.running = False
        self.grblstate = None
        self.modalModes = [
            {'name': 'motion', 'values': ["G80", "G0", "G1", "G2", "G3", "G38.1", "G38.2", "G38.3", "G38.4"]},
            {'name': 'wcs', 'values': ["G54", "G55", "G56", "G57", "G58", "G59"]},
            {'name': 'plane', 'values': ["G17", "G18", "G19"]},
            {'name': 'units', 'values': ["G20", "G21"]},
            {'name': 'distance', 'values': ["G90", "G91"]},
            {'name': 'arc_distance', 'values': ["G90.1", "G91.1"]},
            {'name': 'feed', 'values': ["G93", "G94"]},
            {'name': 'program', 'values': ["M0", "M1", "M2", "M30"]},
            {'name': 'spindle', 'values': ["M3", "M4", "M5"]},
            {'name': 'mist', 'values': ["M7"]},  # Also M9, handled separately
            {'name': 'flood', 'values': ["M8"]}, # Also M9, handled separately
            {'name': 'parking', 'values': ["M56"]}
        ]

    def grbl_parse_status(self, response):
        grbl = {
            'stateName': '',
            'message': '',
            'wco': None,
            'mpos': None,
            'wpos': None,
            'feedrate': 0,
            'spindle': None,
            'spindleSpeed': None,
            'ovr': None,
            'lineNumber': None,
            'flood': None,
            'mist': None,
            'pins': None
        }
        
        response = response.replace('<', '').replace('>', '')
        fields = response.split('|')
        
        for field in fields:
            tv = field.split(':')
            tag = tv[0]
            value = tv[1] if len(tv) > 1 else ''
            
            if tag == "Door":
                self.running = False
                grbl['stateName'] = "Door" + value
                grbl['message'] = field
            elif tag in ["Hold", "Run", "Jog", "Home"]:
                self.running = True
                grbl['stateName'] = tag
            elif tag in ["Idle", "Alarm", "Check", "Sleep"]:
                self.running = False
                grbl['stateName'] = tag
            elif tag == "Ln":
                grbl['lineNumber'] = int(value)
            elif tag == "MPos":
                grbl['mpos'] = list(map(float, value.split(',')))
            elif tag == "WPos":
                grbl['wpos'] = list(map(float, value.split(',')))
            elif tag == "WCO":
                grbl['wco'] = list(map(float, value.split(',')))
            elif tag == "FS":
                fsrates = value.split(',')
                grbl['feedrate'] = float(fsrates[0])
                grbl['spindleSpeed'] = int(fsrates[1])
            elif tag == "Ov":
                ovrates = list(map(int, value.split(',')))
                grbl['ovr'] = {'feed': ovrates[0], 'rapid': ovrates[1], 'spindle': ovrates[2]}
                if not self.OVR or grbl['ovr']['feed'] != self.OVR['feed'] or grbl['ovr']['rapid'] != self.OVR['rapid'] or grbl['ovr']['spindle'] != self.OVR['spindle']:
                    self.OVR = grbl['ovr']
                    self.OVRchanged = True
            elif tag == "A":
                grbl['spindleDirection'] = 'M5'
                for v in value:
                    if v == 'S':
                        grbl['spindleDirection'] = 'M3'
                    elif v == 'C':
                        grbl['spindleDirection'] = 'M4'
                    elif v == 'F':
                        grbl['flood'] = True
                    elif v == 'M':
                        grbl['mist'] = True
            elif tag == "SD":
                sdinfo = value.split(',')
                grbl['sdPercent'] = float(sdinfo[0])
                grbl['sdName'] = sdinfo[1]
                if grbl['stateName'] == "Idle":
                    grbl['stateName'] = "Run"
            elif tag == "Pn":
                grbl['pins'] = value
        
        return grbl

    def grbl_show_state(self):
        if not self.grblstate:
            return
        self.callback.update_state(self.grblstate)

    def grbl_process_status(self, response):
        self.grblstate = self.grbl_parse_status(response)
        
        if self.grblstate['wco']:
            self.WCO = self.grblstate['wco']
        if self.grblstate['ovr']:
            self.OVR = self.grblstate['ovr']
        if self.grblstate['mpos']:
            self.MPOS = self.grblstate['mpos']
            if self.WCO:
                self.WPOS = [v - self.WCO[i] for i, v in enumerate(self.grblstate['mpos'])]
        elif self.grblstate['wpos']:
            self.WPOS = self.grblstate['wpos']
            if self.WCO:
                self.MPOS = [v + self.WCO[i] for i, v in enumerate(self.grblstate['wpos'])]

        self.grbl_show_state()

    def grbl_get_probe_result(self, response):
        tab1 = response.split(":")
        if len(tab1) > 2:
            status = tab1[2].replace("]", "")
            if self.is_probing:
                self.finalize_probing()
            if int(status.strip()) != 1:
                self.callback.probe_failed(self.probe_fail_reason if self.probe_fail_reason else 'Probe Failed')

    def grbl_get_modal(self, msg):
        self.modal['modes'] = msg.replace("[GC:", '').replace(']', '')
        modes = self.modal['modes'].split(' ')
        self.modal['parking'] = None
        self.modal['program'] = ''
        
        for mode in modes:
            if mode == 'M9':
                self.modal['flood'] = mode
                self.modal['mist'] = mode
            else:
                if mode.startswith('T'):
                    self.modal['tool'] = mode[1:]
                elif mode.startswith('F'):
                    self.modal['feedrate'] = mode[1:]
                elif mode.startswith('S'):
                    self.modal['spindle'] = mode[1:]
                else:
                    for modeType in self.modalModes:
                        for s in modeType['values']:
                            if mode == s:
                                self.modal[modeType['name']] = mode
        # self.grbl_show_state()
        self.callback.update_modal(self.modal)

    def handle_message(self, msg):
        if msg.startswith('<'):
            self.grbl_process_status(msg)
            return
        if msg.startswith('[GC:'):
            self.grbl_get_modal(msg)
            return
        if msg.startswith('[MSG: Files changed]'):
            self.callback.refresh_files()
            return
        if msg.startswith('ok'):
            self.callback.handle_ok()
            return
        if msg.startswith('[PRB:'):
            self.grbl_get_probe_result(msg)
            return
        if msg.startswith('[MSG:'):
            return
        if msg.startswith('[JSON:'):
            self.callback.handle_json(msg[6:-1])
            return
        if msg.startswith('error:'):
            self.callback.handle_error(msg)
        if msg.startswith('ALARM:') or msg.startswith('Hold:') or msg.startswith('Door:'):
            if self.is_probing:
                self.callback.probe_failed(msg)
            return
        if msg.startswith('Grbl '):
            self.callback.handle_reset()
            return
