import pyttsx3 as speak

import io
from contextlib import redirect_stdout

from YorkUphysLab.ScoutScale import ScoutSTX
from YorkUphysLab.GwINSTEK import GPD3303D
from YorkUphysLab.Actuator import Actuator
from YorkUphysLab.HVcontrol import HV_control
from YorkUphysLab.Utility import Utility

# See https://pypi.org/project/pyttsx3/ for details on ttsx3

# See https://stackoverflow.com/questions/1218933/can-i-redirect-the-stdout-into-some-sort-of-string-buffer
#   for info about redirecting print outputs (i.e. stdout) to a buffer. Used to get TTS for the setup/close/etc.


# TODO: Add capability for OSCILLOSCOPE (TBS1000 e.g.)

def LookUpType(_key):
    if _key==' grams':
        return ' grams'
    elif _key==' kilovolts':
        return ' kilovolts'
    elif _key==' millimetres':
        return ' millimetres'
    elif _key=='ES':
        return ' grams'
    elif _key=='PSU':
        return ' kilovolts'
    elif _key=='ACT':
        return ' millimetres'
    return ''

class DummyClass:
    def __init__(self):
        self.keyword='None'

dummyClass = DummyClass()

class MyLabMate:
    def __init__(self, _voice=1, _rate='N',_class=dummyClass,_print=True,_comment=None):
        self.engine = speak.init()
        self.voice = _voice
        self.rate = _rate
        self.in_class = _class
        # GET THE KEYWORD
        _key='None'
        if hasattr(self.in_class,'keyword'):
            _key = self.in_class.keyword
        elif hasattr(self.in_class,'HV_on'):
            _key = 'PSU' #HV_Control
        elif hasattr(self.in_class,'actuator_on'):
            _key = 'ACT' #Actuator
        self.config = {'keyword': _key} #For when configurations are used (function generator, oscilloscope, ...)
        self.unit = LookUpType(_key)
        ##################
        self.print = _print
        self.engine.setProperty('voice', self.engine.getProperty('voices')[_voice].id )
        if _rate=='N':
            self.engine.setProperty('rate', 175)
        elif _rate=='S':
            self.engine.setProperty('rate', 125)
        elif _rate=='F':
            self.engine.setProperty('rate', 225)
        else:
            self.engine.setProperty('rate', 175)
        if _comment != None:
            self.comment = _comment
        else:
            self.comment = ""
        if self.config['keyword']=='None':
            self.speak('Beware: you are making a Lab Mate associated with Dummy Class or a class unrecognized by the LabPartner software. Do not expect any further commands to do anything.')

    def loadComment(self,_string,_isReadout=False,_override=None):
        self.comment = str(_string)
        if _isReadout and _override==None:
            self.comment = self.comment+self.unit
        elif _override!=None:
            self.comment = self.comment+_override

    def reset(self):
        _voice = self.voice
        _rate = self.rate
        _unit = self.unit
        del self.engine
        # Set back up the engine
        self.engine = speak.init()
        self.engine.setProperty('voice', self.engine.getProperty('voices')[_voice].id )
        if _rate=='N':
            self.engine.setProperty('rate', 175)
        elif _rate=='S':
            self.engine.setProperty('rate', 125)
        elif _rate=='F':
            self.engine.setProperty('rate', 225)
        else:
            self.engine.setProperty('rate', 175)

    def justspeak(self):
        if self.print:
            print(self.comment)
        self.engine.say(self.comment)
        self.engine.runAndWait()
        self.engine.stop()
        self.reset()

    def speak(self, _string, _isReadout=False):
        self.loadComment(_string, _isReadout)
        self.justspeak()

    def SETUP(self):
        if self.config['keyword'] == 'ES':
            # See StackOverflow link above on the stdout buffer
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.connect()
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'PSU':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.switch_on()
                #self.speak(buf.getvalue())
                print(buf.getvalue())
                self.speak('Power supply text-to-speech misbehaving. I have printed the output to the screen instead.')
            return
        elif self.config['keyword'] == 'ACT':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.switch_on()
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'AFG':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.connect()
                self.speak(buf.getvalue())
            self.speak('The function generator, takes as input via SET the amplitude, frequency, waveform, and offset, as well as whether the output is on or off. The following statements will tell you the configuration.')
            return
        else:
            self.speak('I cannot run setup for the hardware class associated to this Lab Mate.')
            return

    def SET(self, _value):
        if self.config['keyword'] == 'ES':
            self.speak('I cannot run SET for the hardware class associated to this Lab Mate.')
            return
        elif self.config['keyword'] == 'PSU':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.set_hv(_value)
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'ACT':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.set_position(_value)
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'AFG':
            try:
                if _value[0]=='V' or _value[0]=='v':
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.in_class.set_amplitude(_value[1])
                        self.config['amplitude'] = str(_value[1])+' Volts'
                        self.speak(buf.getvalue())
                    return
                if _value[0]=='F' or _value[0]=='f':
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.in_class.set_frequency(_value[1])
                        self.config['frequency'] = str(_value[1])+' Hertz'
                        self.speak(buf.getvalue())
                    return
                if _value[0]=='W' or _value[0]=='w':
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.in_class.set_waveform(_value[1])
                        self.config['waveform'] = str(_value[1])
                        self.speak(buf.getvalue())
                    return
                if _value[0]=='O' or _value[0]=='o':
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.in_class.set_DCoffset(_value[1])
                        self.config['offset'] = str(_value[1])+' Volts'
                        self.speak(buf.getvalue())
                    return
                if _value[0]=='ON' or _value[0]=='on' or _value[0]=='On':
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.in_class.set_output("ON")
                        self.config['state'] = 'ON'
                        self.speak(buf.getvalue())
                    return
                if _value[0]=='OFF' or _value[0]=='off' or _value[0]=='Off':
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.in_class.set_output("OFF")
                        self.config['state'] = 'OFF'
                        self.speak(buf.getvalue())
                    return
            except:
                self.speak('For the function generator, the input value to set should be a two item list. A character "V" to see amplitude, "F" to set frequency, "W" for waveform, and "O" for offset. Second value is the valuue to set. A list with "ON" as first element turns on the output, while "OFF" turns it off.')
                return
        else:
            self.speak('I cannot run SET for the hardware class associated to this Lab Mate.')
            return

    def GET(self):
        if self.config['keyword'] == 'ES':
            # See StackOverflow link above on the stdout buffer
            with io.StringIO() as buf, redirect_stdout(buf):
                weight = self.in_class.read_weight()
                self.speak(buf.getvalue())
            self.speak( weight, True )
            return
        elif self.config['keyword'] == 'PSU':
            with io.StringIO() as buf, redirect_stdout(buf):
                voltage = self.in_class.get_hv()
                self.speak(buf.getvalue())
            self.speak( voltage, True )
            return
        elif self.config['keyword'] == 'ACT':
            with io.StringIO() as buf, redirect_stdout(buf):
                position = self.in_class.get_position()
                self.speak(buf.getvalue())
            self.speak( position, True )
            return
        elif self.config['keyword'] == 'AFG':
            self.speak('Your current user-defined settings are as follows:')
            for key in self.config.keys():
                statement = key + ' is ' + str(self.config[key])
                self.speak(statement)
            self.speak('The device is set up in the following manner:')
            keyList=['FREQ','AMPL','VOLT:UNIT','FUNC','DCO','OUTP']
            nameDict={'FREQ':'Frequency', 'AMPL':'Amplitude', 'VOLT:UNIT':'Amplitude format',
                      'FUNC':'Function', 'DCO':'DC Offset', 'OUTP':'Output' }
            unitDict={'FREQ':'Hz', 'AMPL':'V', 'VOLT:UNIT':'', 'FUNC':'', 'DCO':'V', 'OUTP':'' }
            try:
                for key in keyList:
                    # Based on the *IDN? command used in YorkUphysLab and a Gemini suggestion about the meaning of "?"
                    # I tried to probe some values directly in the SOUR1:ITEM style it is using to SET things in
                    # YorkUphysLab and found this largely seems to work. Let's use this to print things out now.
                    command=f'SOUR1:{key}?'
                    self.in_class.inst.write(command.encode('ascii') + b'\r\n')
                    readout=self.in_class.inst.readline().strip().decode('ascii')
                    self.speak( nameDict[key]+' is '+readout+unitDict[key] )
            except:
                self.speak('There was an error reading device.')
            return
        else:
            self.speak('I cannot run GET for the hardware class associated to this Lab Mate.')
            return

    def CLOSE(self):
        if self.config['keyword'] == 'ES':
            # See StackOverflow link above on the stdout buffer
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.close_connection()
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'PSU':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.switch_off()
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'ACT':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.switch_off()
                self.speak(buf.getvalue())
            return
        elif self.config['keyword'] == 'AFG':
            with io.StringIO() as buf, redirect_stdout(buf):
                self.in_class.close()
                self.speak(buf.getvalue())
            return
        else:
            self.speak('I cannot run GET for the hardware class associated to this Lab Mate.')
            return
