from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from flask import Flask, render_template, Response, request
from io import BytesIO
import matplotlib.pyplot as plt
import os
import subprocess
from scipy.interpolate import griddata
import numpy as np
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/run/srt', methods=['get'])
def runSRTExecutable():
    """
    Run SRT.exe, and return processing status
    """
    inputFolder = './srt/000input/'
    outputFolder = './srt/000output/'
    inputFile = inputFolder + 'InputsForSRT_Comb.txt'

    # create the folder
    if not os.path.exists(inputFolder):
        os.mkdir(inputFolder)
    # check the input file
    if not os.path.exists(inputFile):
        return "Error: Input file does not exist!"
    # create the folder
    if not os.path.exists(outputFolder):
        os.mkdir(outputFolder)
    # remove the exist file in output folder 
    for f in os.listdir(outputFolder):
        os.remove(os.path.join(outputFolder, f))

    try:
        subprocess.run(['./srt/SRT-HS2.exe'], cwd='./srt')
        return "execution completed and start drawing..."
    except subprocess.CalledProcessError as e:
        return "Error: {}".format(e.returncode)


@app.route('/api/save/file', methods=['POST'])
def saveAsFile():
    """
    Save the parameter in a txt file, return processing status
    """
    if request.method == "POST":

        i0 = request.form['i0']
        sza = request.form['SZA']
        azimuth = request.form['azimuth']
        treeType = request.form['treeType']
        h = request.form['H']
        d_l = request.form['D_L']
        diam = request.form['diam']
        vegCover = request.form['vegCover']
        hotspot = request.form['hotspot']
        tau_L = request.form['tau_L']
        ro_L = request.form['ro_L']
        iorien = request.form['iorien']
        ro_Soil = request.form['ro_Soil']
        ifren = request.form['ifren']
        refind = request.form['refind']
        sk = request.form['sk']
        slope = request.form['slope']
        aspect = request.form['aspect']
        numberOfLayers = request.form['numberOfLayers']
        epsiter = request.form['epsiter']
        maxiter = request.form['maxiter']
        total_Number = request.form['total_Number']
        coordFlag = request.form['coordFlag']
        zenith = request.form['zenith']
        zenithInterval = request.form['zenithInterval']
        azimuthInterval = request.form['azimuthInterval']


        filename = "InputsForSRT_Comb.txt"
        f = open(os.path.join('./srt/000input/', filename), 'w')
        f.write("1.Canopy Info." + '\n')
        f.write("# i0(0-1)    SZA(degree)   azimuth(degree)   TreeType    H    d_L    diam    VegCover  HotSpot" + '\n')
        f.write(i0 + '\t' + sza + '\t' + azimuth + '\t' + treeType + '\t' +
                h + '\t' + d_l + '\t' + diam + '\t' + vegCover + '\t' + hotspot)
        f.write('\n')

        f.write("2.Leaf and Soil Info." + '\n')
        f.write("# tau_L     ro_L   iorien   ro_Soil      ifren   refind     sk" + '\n')
        f.write(tau_L + '\t' + ro_L + '\t' + iorien + '\t' +
                ro_Soil + '\t' + ifren + '\t' + refind + '\t' + sk)
        f.write('\n')

        f.write("3.Topography Info.(degree)" + '\n')
        f.write("# Slope    Aspect" + '\n')
        f.write(slope + '\t' + aspect)
        f.write('\n')

        f.write("4.Configuration Para" + '\n')
        f.write("# NumberOfLayers    epsiter    maxiter  !desired relative accuracy and max # of iterations" + '\n')
        f.write(numberOfLayers + '\t' + epsiter + '\t' + maxiter)
        f.write('\n')

        f.write("5.View Angles(degree)" + '\n')
        f.write("# Total_Number  CoordFlag" + '\n')
        f.write(total_Number + '\t' + coordFlag)
        f.write('\n')

        f.write("# L1=Zenith    L2=Azimuth" + '\n')
        azimuth_temp = [i for i in range(0, 360, int(azimuthInterval))]

        zenith_temp = []
        for j in range(0, int(zenith)+int(zenithInterval), int(zenithInterval)):
            zenith_temp.append(j)
        
        # write the zenith
        for k in zenith_temp:
            count = 0
            while(count < len(azimuth_temp)):
                f.write(str(k) + '\t')
                count += 1
        f.write('\n')

        # write the azimuth
        for m in range(len(zenith_temp)):
            for n in azimuth_temp:
                f.write(str(n) + '\t')

        f.write('\n')

        f.close()
        return "Save file success!"


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    if "Cache-Control" not in response.headers:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response


@app.route('/api/show/figure')
def figure():
    """
    Return the Response object with the value of BytesIO objects
    """
    fig = create_figure()
    output = BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    """
    Draw and return the figure
    """
    outputFolder = './srt/000output/'

    Angles = []
    Radii = []
    Values = []

    for f in os.listdir(outputFolder):
        if f == "FinalHDRF_BSplusS.txt":
            with open(outputFolder + f, 'r') as file:
                for line in file:
                    # Split on any whitespace (including tab characters)
                    row = line.split()
                    try:
                        row[4], row[5], row[10] = float(
                            row[4]), float(row[5]), float(row[10])
                        Radii.append(row[4])
                        Angles.append(row[5])
                        Values.append(row[10])
                    except ValueError:
                        pass

    Angles = np.array(Angles) / 180. * np.pi
    x = np.array(Radii) * np.sin(Angles)
    y = np.array(Radii) * np.cos(Angles)

    Xi = np.linspace(min(x), max(x), 600)
    Yi = np.linspace(min(y), max(y), 600)

    # make the axes
    fig = plt.figure()
    left, bottom, width, height = [-0.1, 0.1, 1, 0.7]
    ax = plt.axes([left, bottom, width, height])
    pax = plt.axes([left, bottom, width, height],
                   projection='polar',
                   facecolor='none')
    pax.set_theta_zero_location('N')
    pax.set_theta_direction(-1)
    pax.set_rlabel_position(12)
    pax.set_rmax(max(Radii))
    pax.set_rmin(min(Radii))
    pax.set_thetagrids(np.arange(0.0, 360.0, 30.0))
    cax = plt.axes([0.75, 0.1, 0.05, 0.7])
    ax.set_aspect(1)
    ax.axis('Off')

    # grid the data
    Vi = griddata((x, y), Values, (Xi[None, :], Yi[:, None]), method='cubic')
    cf = ax.pcolormesh(Xi, Yi, Vi, cmap=plt.cm.jet) # draw the colormesh
    cf1 = ax.contour(Xi, Yi, Vi, 8, colors='k') # draw the contour
    # ax.clabel(cf1, fontsize=8, inline=True) # show the the contour value
    plt.figtext(0.4, 0.9, 'FinalHDRF_BSplusS', ha='center') # set figure title
    plt.colorbar(cf, cax=cax, ax=ax) # draw the colorbar
    return fig


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
