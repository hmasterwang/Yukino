import sys
import datetime
from collections import defaultdict

class Pixel(object):
    '''Pixel data in each step'''
    def __init__(self):
        self._row = None
        self._col = None
        self._adc = None
        self._reg = None

    def __init__(self, row, col, adc, reg):
        self._row = row
        self._col = col
        self._adc = adc
        self._reg = reg

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

    @property
    def reg(self):
        '''Register'''
        return self._reg

# Start
def main():
    if len(sys.argv) < 3:
        print 'python ./Yukino inputfile outfile'
        sys.exit(1)

    with open(sys.argv[1]) as f:
        content = f.readlines()
        content = [x.strip('\n') for x in content]
        # We process high range only
        lowRanges = content[1].split()[2:]
        lowRanges = [int(int(x) / 7. - 1) if int(x) % 7. < 0.5 else int(int(x) / 7. + 1) for x in lowRanges]
        highRanges = content[2].split()[2:]
        highRanges = [int(int(x) / 7. - 1) if int(x) % 7. < 0.5 else int(int(x) / 7. + 1) for x in highRanges]

        fullList = defaultdict(list)

        print('High Ranges: ')
        for highr in highRanges:
            print(highr),
        print('\n'),

        print('Reading gain calibration...')
        # Pixel w/ multiple scan vcals
        for line in content[4:]:
            if line.isspace():
                continue
            
            pixelData = line.split()
            row = pixelData[-2]
            col = pixelData[-1]
            sys.stdout.write('.')

            # High Ranges * 7
            pixelData[len(lowRanges): -3] = [int(x) * 7 for x in  pixelData[len(lowRanges): -3]]

            calibs = zip(lowRanges + highRanges, pixelData)

            # Remove duplicated reg
            seen = set()
            seen_add = seen.add
            calibs = [ x for x in calibs if not (x[0] in seen or seen_add(x[0]))]

            for calib in calibs:
                pix = Pixel(int(row), int(col), int(calib[1]), int(calib[0]))
                fullList[calib[0]].append(pix)
        print('\n')

        with open(sys.argv[2], 'w+') as outf:
            print('Writing gain calibration...')
            keys = sorted(fullList.keys(), cmp = lambda x, y: cmp(int(x), int(y)))
            outf.writelines([ 
                datetime.datetime.now().strftime('%H:%M:%S on %A, %B %d, %Y\n'),
                'User Note: Gain\n',
                '---------------------- 1 Register ---------------------------------\n',
                'CC_ALIAS: digital\n',
                'CID: 0\n',
                'REG: 25. Vcal-25\n',
                'START: 0\n',
                'STEP: 5\n',
                'ITERATIONS: %d\n' % (len(keys)),
                'TIME_TO_READ: 10\n',
                'NUM_OF_PIX: 4\n',
                'INJECT_NUM: 10\n',
                'INJECT_PER: 400\n',
                'MAX_ADC: 1024\n',
                '----------------------------------------------------------------------\n'])
            for idx, key in enumerate(keys):
                idx += 1
                print('Writing iteration %d Vcal %s' % (idx, key))
                outf.write('Iteration %d --- reg = %d\n' % (idx, int(key)))
                for pix in fullList[key]:
                    # Invalid pulse height
                    if (pix.adc < 0 and pix.adc != -9999):
                        continue
                    outf.write('r %d c %d h 0 a %d\n' % (pix.row, pix.col, pix.adc))

            outf.flush()


if __name__ == "__main__":
    main()