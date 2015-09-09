import sys
import datetime
from collections import defaultdict

class Pixel(object):
    '''Pixel data in each step'''
    def __init__(self):
        self._row = None
        self._col = None
        self._adc = None


    def __init__(self, row, col, adc):
        self._row = int(row)
        self._col = int(col)
        self._adc = int(adc)


    @property
    def col(self):
        '''Column'''
        return self._col

    @property
    def row(self):
        '''Row'''
        return self._row

    @property
    def adc(self):
        '''ADC Value'''
        return self._adc


# Start
def main():
    if len(sys.argv) < 3:
        print('python ./Yukino inputfile outfile')
        sys.exit(1)

    with open(sys.argv[1]) as f:
        content = f.readlines()
        content = [x.strip('\n') for x in content]
        # We process high range only
        lowRanges = content[1].split()[2:]
        highRanges = content[2].split()[2:]
        fullList = defaultdict(list)

        # Read and populate
        print('Reading gain calibration...')

        # Step calculation


        # Pixel w/ multiple scan vcals
        for line in content[4:]:
            if line.isspace():
                continue
            
            pixelData = line.split()
            row = pixelData[-2]
            col = pixelData[-1]
            sys.stdout.write('.')

            #
            highRangeData = pixelData[len(lowRanges): -3]

            for i in range(0, len(highRangeData)):
                fullList[int(highRanges[i])].append(Pixel(row, col, highRangeData[i]))

        



        with open(sys.argv[2], 'w+') as outf:
            print('Writing gain calibration...')
            keys = sorted(fullList.keys())
            min = keys[0]
            max = keys[-1]
            keyidx = 0;
            iteration = 0;

            outf.writelines([ 
                datetime.datetime.now().strftime('%H:%M:%S on %A, %B %d, %Y\n'),
                'User Note: Gain\n',
                '---------------------- 1 Register ---------------------------------\n',
                'CC_ALIAS: digital\n',
                'CID: 0\n',
                'REG: 25. Vcal-25\n',
                'START: %d\n' %(keys[0]),
                'STEP: 10\n',
                'ITERATIONS: %d\n' % ((max - min) / 10 + 1),
                'TIME_TO_READ: 10\n',
                'NUM_OF_PIX: 4\n',
                'INJECT_NUM: 10\n',
                'INJECT_PER: 400\n',
                'MAX_ADC: 1024\n',
                '----------------------------------------------------------------------\n'])


            while keyidx != len(keys):
                iteration += 1
                reg = min + (iteration - 1) * 10
                outf.write('Iteration %d --- reg = %d\n' % (iteration, reg))

                if keys[keyidx] == reg:
                    keyidx += 1
                else:
                    continue

                print('Writing iteration %d reg %s' % (iteration, reg))
                
                for pix in fullList[reg]:
                    # Invalid pulse height
                    if (pix.adc < 0):
                        continue
                    outf.write('r %d c %d h 1 a %d\n' % (pix.row, pix.col, pix.adc * 4))

            outf.flush()


if __name__ == "__main__":
    main()