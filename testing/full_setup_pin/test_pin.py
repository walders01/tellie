import time
import ROOT
from core import serial_command
import sys

sc = serial_command.SerialCommand('/dev/ttyS0')

channels = range(1,97)
try:
    channels = [int(sys.argv[1])]
    print "RUNNING CHANNEL",channels
except:
    pass
#channels = [10]
#channels = [60]
#channels = []
#for i in range(4):
#    channels.append(i*4+1)
#channels = [60,65,70,75]
print channels
widths = range(0,6000,200)

#######################################
#for the branches
ROOT.gROOT.ProcessLine(\
    "struct Results{\
        Int_t width;\
        Int_t pin;\
     };")
from ROOT import Results
results = Results()
########################################

tc = ROOT.TCanvas("can","can")


sc.select_channel(channels[0])
sc.set_pulse_height(16383)
sc.set_pulse_delay(1.0)
sc.set_pulse_number(1000)
sc.set_fibre_delay(0)
sc.set_trigger_delay(0)
sc.disable_external_trigger()
sc.set_pulse_width(16383)
sc.fire()
time.sleep(1)
pin = None
while pin==None:
    pin = sc.read_pin()
print "DARK FIRE OVER: PIN",pin
time.sleep(1)

for channel in channels:

    print "running channel",channel
    
    t_str = time.strftime('%y%m%d_%H.%M')
    fname = "results/pin_width_ch%02d_%s.root"%(channel,t_str)
    tf = ROOT.TFile(fname,"recreate")

    tt = ROOT.TTree("T","T")
    tt.Branch("width",ROOT.AddressOf(results,"width"),"width/I")
    tt.Branch("pin",ROOT.AddressOf(results,"pin"),"pin/I")

    tg = ROOT.TGraph()
    tg.SetMarkerStyle(23)
    tg.GetXaxis().SetTitle("IPW")
    tg.GetYaxis().SetTitle("PIN")
    tg.SetTitle("Channel %02d"%channel)

    sc.clear_channel()
    sc.select_channel(channel)
    sc.set_pulse_height(16383)
    sc.set_pulse_delay(1.0)
    sc.set_pulse_number(1000)
    sc.set_fibre_delay(0)
    sc.set_trigger_delay(0)
    sc.disable_external_trigger()
    
    ipt = 0

    for width in widths:
        sc.set_pulse_width(width)
        sc.fire()
        time.sleep(1.0)
        pin = None
        while pin==None:
            pin = sc.read_pin()
        results.pin = int(pin)
        results.width = width
        tt.Fill()
        tg.SetPoint(ipt,float(width),float(pin))
        print "WIDTH:",width,"PIN",pin
        ipt += 1
        tg.Draw("ap")
        tc.Update()
    
#    raw_input("wait")

    tt.Write()
    tf.Close()
        
        
