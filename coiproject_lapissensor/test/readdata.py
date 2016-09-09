import json
import cPickle as pickle
import csv

f = open('pupil_data', 'rb')
data = f.read()

loaded_data = pickle.loads(data)
rows = []

for item in loaded_data['gaze_positions']:
    p, = item["base"]

    data_2d = ['%s' % p['timestamp'], p['id'], p['confidence'],
               p['norm_pos'][0], p['norm_pos'][1], p['diameter']]
    # p['method']]
    try:
        ellipse_data = [p['ellipse'][0][0], p['ellipse'][0][1],
                        p['ellipse'][1][0], p['ellipse'][1][1], p['ellipse'][2]]
    except KeyError:
        ellipse_data = [None, ] * 5

    rows.append(data_2d + ellipse_data)

# print (loaded_datSa)

with open(('pupil_postions.csv'),'wb') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(('timestamp',
                        'id',
                        'confidence',
                        'norm_pos_x',
                        'norm_pos_y',
                        'diameter',
                        'method',
                        'ellipse_center_x',
                        'ellipse_center_y',
                        'ellipse_axis_a',
                        'ellipse_axis_b',
                        'ellipse_angle'))
    for row in rows:
        csv_writer.writerow(row)

