import serial
import time
import sys

serial_port = 'COM3'
baud_rate = 38400

# Establish a connection to the serial port
ser = serial.Serial(serial_port, baud_rate, timeout=1)
ser.set_buffer_size(rx_size = 4096, tx_size = None)


try:
    rec = False
    recodsCount = 0
    recodeCollecter = ''
    while True:
        # Read data from the serial port
        data = ser.readline().decode('utf-8')

        # If data received, print it
        if data:
            c = data[0]
            if c == 'x':
                try:
                    x,y,z = data.split(',')[:3]
                    x = float(x.split(':')[1])
                    y = float(y.split(':')[1])
                    z = float(z.split(':')[1])
                    if rec:
                        recode = "\nx: %+011.6f , y: %+011.6f , z: %+011.6f" % (x,y,z)
                        sys.stdout.write(recode)
                        sys.stdout.flush()
                        recodeCollecter += recode
                    else:
                        sys.stdout.write("\rx: %+011.6f\ty: %+011.6f\tz: %+011.6f" % (x,y,z))
                        sys.stdout.flush()
                except:
                    pass
            if c == 'a':
                try:
                    if rec:
                        x,y,z = data.split(',')[:3]
                        x = int(x.split(':')[1])
                        y = int(y.split(':')[1])
                        z = int(z.split(':')[1])
                        recode = ", ax: %d , ay: %d , az: %d" % (x,y,z)
                        # sys.stdout.write(recode)
                        # sys.stdout.flush()
                        recodeCollecter += recode
                        
                except:
                    pass
            if data[:5] == 'Index':
                try:
                    if rec:
                        ind = int(data.split(':')[1])
                        recodeCollecter += ', index: '+str(ind)
                        recodsCount +=1
                        if recodsCount==100:
                            f = open('recodes.csv','a')
                            f.write(recodeCollecter+'\n\n')
                            rec = False
                except:
                    pass
            if data[:3] == 'rec':
                print("\nrecoding...")
                rec = True
                recodsCount = 0
                recodeCollecter = ''
            #print("Received data from serial port: ", data)
            # Give the device time to send data again
            # time.sleep(0.001)

# To close the serial port gracefully, use Ctrl+C to break the loop
except KeyboardInterrupt:
    print("Closing the serial port.")
    ser.close()
