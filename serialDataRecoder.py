import serial
import time
import sys

TARGET_DRUM = ', 0'

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
        try:
            data = ser.readline().decode('utf-8')
        except:
            print("decode Error")
            continue;
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
                        # recode = "\n%.6f , %.6f , %.6f" % (x,y,z) 
                        recode = "%d , %d , %d " % (x,y,z)
                        sys.stdout.write(recode+"\n")
                        sys.stdout.flush()
                        recodeCollecter += recode
                    else:
                        # sys.stdout.write("\rx: %+011.6f\ty: %+011.6f\tz: %+011.6f" % (x,y,z))
                        sys.stdout.write("\rx: %5d\ty: %5d\tz: %5d" % (x,y,z))
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
                        recode = ", %d , %d , %d , " % (x,y,z)
                        # sys.stdout.write(recode)
                        # sys.stdout.flush()
                        recodeCollecter += recode
                        recodsCount +=1
                        if recodsCount==39:
                            recode += recode[:-2]+'\n'
                            f = open('recodes.csv','a')
                            f.write(recodeCollecter+'\n\n')
                            rec = False
                        
                except:
                    pass

            if data[:3] == 'rec' and rec == False:
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
