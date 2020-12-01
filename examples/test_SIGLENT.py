import pyvisa as visa

def main():
    _rm = visa.ResourceManager()
    sds = _rm.open_resource("USB0::62700::60984::SDSMMEBD2R5477::0::INSTR")
    sds.write("chdr off")
    vdiv = sds.query("c1:vdiv?")
    ofst = sds.query("c1:ofst?")
    div = sds.query("tdiv?")
    sara = sds.query("sara?")
    sara = float(sara.rstrip('\x00'))

    sds.timeout = 30000 #default value is 2000(2s)
    sds.chunk_size = 20*1024*1024 #default value is 20*1024(20k bytes)
    recv = sds.query("c1:wf?")
    recv = list(sds.read_raw())[15:]
    print(recv)

    recv.pop()

    """
    recv.pop()
    volt_value = []
    for data in recv:
        if data > 127:
            data = data - 255
        else:
            pass
        volt_value.append(data)
    time_value = []
    for idx in range(0,len(volt_value)):
        volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
        time_data = -(float(tdiv)*14/2)+idx*(1. / sara)
        time_value.append(time_data)
    pl.figure(figsize=(7,5))
    pl.plot(time_value,volt_value,markersize=2,label=u"Y-T")
    pl.legend()
    pl.grid()
    pl.show()
    """


if __name__=='__main__':
    main()
