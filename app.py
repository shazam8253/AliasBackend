from flask import Flask, request, jsonify
from flask_cors import CORS
from pinatapy import PinataPy
pinata = PinataPy('75ebb8229d0e436e9672', '9e8cfa0a9db4f7a7d07eb67d03514dd8e0bd24066ac44b5d5af698ac5d8bfe4c')
import json
import subprocess
import os, os.path
import glob
import shutil

def remove_thing(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def empty_directory(path):
    for i in glob.glob(os.path.join(path, '*')):
        remove_thing(i)


app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = '.\pifuhd\sample_images'





@app.route('/getAIias', methods=['POST'])
def run_command():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    pkey = request.form['pkey']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'img.jpg'))
        
    command = 'python preprocess.py'
    subprocess.run(command, shell=True, text=True, cwd='./lightweight-human-pose-estimation.pytorch')
    result = subprocess.run('python -m apps.simple_test -r 256 --use_rect -i .\sample_images', shell=True, text=True, cwd='./pifuhd')
    filnameobj = 'peep{}.obj'.format(pkey)
    filnameimg = 'peep{}.png'.format(pkey)
    metadataname = 'peep{}meta.json'.format(pkey)
    response1 = pinata.pin_file_to_ipfs(path_to_file='pifuhd/results/pifuhd_final/recon/result_img_256.obj', ipfs_destination_path=filnameobj, save_absolute_paths=False)
    ipfshash1 = response1['IpfsHash']
    response2 = pinata.pin_file_to_ipfs(path_to_file='pifuhd/results/pifuhd_final/recon/result_img_256.png', ipfs_destination_path=filnameimg, save_absolute_paths=False)
    ipfshash2 = response2['IpfsHash']
    dict = { "description": "An AI generated 3D model of a human", "external_url": "ipfs://{}".format(ipfshash1), "image": "ipfs://{}".format(ipfshash2), "name": "Whatever", "attributes": [] }
    json.dump(dict, open(metadataname, 'w'))
    response = pinata.pin_file_to_ipfs(path_to_file=metadataname, ipfs_destination_path=metadataname)
    empty_directory('pifuhd/results/pifuhd_final/recon')
    empty_directory('pifuhd/sample_images')
    remove_thing(metadataname)    
    return jsonify(response), 200


if __name__ == '__main__':
    app.run(debug=True)