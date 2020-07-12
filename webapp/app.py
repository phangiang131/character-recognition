# -*- coding: utf-8 -*-
# coding: utf-8
import os
from azure.storage.blob import BlockBlobService
import cv2
import numpy as np
from flask import Flask, request, redirect, url_for,render_template
from werkzeug.utils import secure_filename
import cv2
import requests
import time
import random
import requests
import shutil
import numpy as np
import logging
import requests
import json
import cv2
from random import randint

from utils import *


account_name = 'animefacerecog'
account_key = 'uHDXGLKui5bjKWCIoTERMLnJYL8M+hSRtgta8/PJvVdguIS4Gl+ukaU+cBO+zhNt9M5RE+V37PA7oJOW6jlCCg=='
block_blob = BlockBlobService(account_name,account_key)

if not os.path.exists('anime_mapping.json'):
    block_blob_service.get_blob_to_path('yolomodel','anime_mapping.json','anime_mapping.json')
    block_blob_service.get_blob_to_path('yolomodel','anime_data.json','anime_data.json')
    block_blob_service.get_blob_to_path('yolomodel','image_href_mapping.json','image_href_mapping.json')
    block_blob_service.get_blob_to_path('yolomodel','data_classes.json','data_classes.json')

with open('anime_mapping.json') as f:
    anime_mapping = json.load(f)
with open('anime_data.json') as f:
    anime_database = json.load(f)
with open('image_href_mapping.json') as f:
    image_mapping = json.load(f)
with open('data_classes.json') as f:
    data_classes = json.load(f)

UPLOAD_FOLDER = '.'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        # check if the post requesyt has the file part

        if 'uploaded_image' not in request.files:
            return redirect(request.url)

        file = request.files['uploaded_image']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            image = np.fromstring(file.read(), dtype='uint8')
            image = cv2.imdecode(image, -1)
            
            file.close()
            ran_im = randint(0,10**8)
            res, im_png = cv2.imencode('.png', image)
            block_blob.create_blob_from_bytes('animeimage',f'{ran_im}.png',im_png.tobytes())
            
            res = requests.get(f'https://animefacerecog.azurewebsites.net/api/animeyolo?code=eYTVzF7DGnpxEy2lU9PEXehsl4AuXxUizan3re33aaA4JeHKCMyhYQ==&imagepath={ran_im}.png')
            bouding_box = json.loads(res.content)['bouding_box']

            result_dict = {}
            for b in bouding_box:
                crop = image[b[1]:b[1]+b[3],b[0]:b[0]+b[2]]
                res, im_png = cv2.imencode('.png', crop)
                ran = randint(0,10**8)
                block_blob.create_blob_from_bytes('animeimage',f'{ran}.png',im_png.tobytes())
                res = requests.get(f'https://animefacerecog.azurewebsites.net/api/animegetname?code=6fTQb2ZK7qXx/UL5lj1HnFX6pnJvAo4dsawijx5xLFhoI6q8WtyW5g==&imagepath={ran}.png')
                result_dict[f'{ran}'] = json.loads(res.content)
                result_dict[f'{ran}']['url'] = block_blob.make_blob_url('animeimage',f'{ran}.png')


            # return (str(label_dict))
            
            count = 0
            text = ''
            height_1 = 0

            for k in result_dict.keys():
                r = result_dict[k]
                count +=1
                text += '<div style="font-size: 300%;">Input</div>'
                text = text+"<img src ={} height=300 width=300>".format(r['url'])
    
                text += '<div style="font-size: 300%;">Output</div>'
                for label in r['label']:
                    name, anime_name = label.split(':')
                    
                    text += "<div>"

    
                    anime_data = get_anime_data(anime_name,anime_mapping,anime_database)
                    
                    image_character_id = get_image_character_src(name,anime_data,image_mapping)


                    text += "<img src=https://animefacerecog.blob.core.windows.net/animeface/{}.jpg height=100 width=100> {} ".format(image_character_id,name)
                    
    
                    
                    x = '<br>'
                    height_1 += 1
                    x = x +'''
<div class="anime"><a href="">{}</a>
    <div class="anime-info">Anime Detail
        <div class="card1" style="width: 12rem; ">
            <img class="card-img-top" src=https://animefacerecog.blob.core.windows.net/animecover/{}.jpg alt="Card image cap">

            <ul class="list-group list-group-flush">
                <li class="list-group-item">Alt Name: {}</li>
                <li class="list-group-item">Eps: {}</li>
                <li class="list-group-item">Studio: {}</li>
                <li class="list-group-item">Year: {}</li>
                <li class="list-group-item">Season: {}</li>
            </ul>
        </div>
    </div>
</div>
                        '''.format(anime_data['name'],anime_data['cover_id'],anime_data['alt_name'],anime_data['eps'],anime_data['studio']['name'],anime_data['year'],anime_data['year'])
  
                    x += '<br>'
                                      
                    text += "{}</div>".format(x)
            height = 300+ 1000*count+height_1*17
            
            return '''
<!doctype html>
<html lang="en">

<head>
    <title>Project Anime X</title>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>

<body>
    <!-- HEADER START-->
    <header id="header">
        <div class="content">
            <div id="logo"><a href="#home">NON-OTAKU GROUP </a></div>
            <nav id="nav">
                <ul id="slidenav">
                    <li><a href="#home" class="active" title="Oxana Web">Home</a></li>
                    <li><a href="#about" title="About">Search</a></li>
                    <li><a href="#services" title="Services">Tutorial</a></li>
                    
                    <li><a href="#contact" title="Contact">Contact</a></li>
                </ul>
                <ul id="slidenavdesktop">
                    <li><a href="#home" class="active" title="Next Section">Home</a></li>
                    <li><a href="#about" title="Next Section">Search</a></li>
                    <li><a href="#services" title="Next Section">Tutorial</a></li>
                    
                    <li><a href="#contact" title="Next Section">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>
    <!-- SLIDES START -->
    <div id="home">
        <div class="content">
            <h1><strong>ANIME FINDER</strong></h1>
            <b>Finding any Anime Characters by Images</b>
            <br/>
            <br/>
            <img src="https://storage.googleapis.com/animeprojectx.appspot.com/rem.jfif" alt="Smiley face" width="165" >
            <div id="divider"> </div>

            <a href="#about">
                <div id="button">
                    <h3>START</h3>
                </div>
            </a>
            <div id="arrow"></div>
        </div>
    </div>
    <div id="about">
        <div class="uploadArea">
            <div class="col-md-8">
                <h4 class="mb-3">Upload Image</h4>
                <form method="POST" enctype="multipart/form-data">
                    <div class="col-md-6 md-3">
                        <input type="file" name="uploaded_image" accept="image/*" onchange="loadFile(event)">
                        <div><small class="text-muted">Accepted mime-type: image/jpeg, image/png</small></div>
                    </div>
                    
                    <button class="btn btn-primary btn-lg btn-block" type="submit">Upload</button>
                </form>
            </div>
            <img id="img">
        </div>
        {}
    </div>
    <div id="services">
        <div class="content">
            <div class="quotes_container">
                <p class="quotes">Ứng dụng hỗ trợ tìm kiếm các nhân vật anime thông qua khuôn mặt.</p>
                <p class="quotes">Ấn nút <b class = "redtext">Chọn tệp</b>, chọn ảnh rồi bấm <b class = "redtext">Upload</b>. Đợi 40s đến 1p là web sẽ trả về top 5 nhân vật gần giống nhất kèm thêm 1 số thông tin của nhân vật.</p>
                
                <p class="quotes">Hiện tại ứng dụng có thể nhận diện khoảng 550 nhân vật của các bộ trong <a href="/lists" class = "redtext"><u>danh sách</u></a> với độ chính xác là 98% (trong điều kiện tốt nhất), ảnh có một hoặc nhiều nhân vật đều dùng được. </p>
                <p class="quotes">Bên cạnh các ảnh chứa các nhân vật trong anime, ứng dụng cũng có thể nhận diện nhân vật thông qua fan art, figure, cosplay,... nhưng với độ chính xác thấp hơn. </p>
                <p class="quotes">Hướng dẫn sử dụng <a href="https://animeprojectx.appspot.com/beta" class = "redtext"><u>phiên bản beta</u></a>: </p>
                <p class="quotes">- Phiên bản beta giúp dùng người dùng tạo khung chứa khuôn mặt rồi upload. Nhờ vậy mà độ chính xác tăng đáng kể và thời gian xuống khoảng 20s. Nhưng do dùng hơi bất tiện nên có tên là beta :v. </p>
                <p class="quotes">- Ấn nút <b class = "redtext">Chọn tệp</b>, rồi chọn ảnh. Sau đó ảnh sẽ hiện lên trên trình duyệt. Người dùng click vào ảnh để tạo các khung chứa khuôn mặt cần nhận diện(có thể 1 hoặc nhiều khung) rồi ấn <b class = "redtext">Upload</b>. </p>
                <p class="quotes">- Nếu muốn dùng tiếp thì người dùng phải <b class = "redtext">reload</b> lại trang. </p>
                
            </div>
        </div>
    </div>

    <div id="contact">
        <div class="content">
            <div class="contact_container">


                
                <div id="social">
                    <a class="facebookBtn smGlobalBtn" href="https://www.facebook.com/thegiang.phan"></a>

                </div>

            </div>
            
        </div>
    </div>
    <!-- SLIDES END -->
</body>
<!-- Optional JavaScript -->
<!-- jQuery first, then Popper.js, then Bootstrap JS -->
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>

<link rel="stylesheet" type="text/css" href="/static/style_x.css">
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>


<script>
        document.getElementById("about").style.height = {} + "px";
        var loadFile = function(event) {{
        var output = document.getElementById('img');
        output.src = URL.createObjectURL(event.target.files[0]);
        var img = new Image();
        img.src = output.src;
        img.onload = function() {{
            var height = img.height;
            var width = img.width;


            document.getElementById("about").style.height = height + {} + "px";
            // code here to use the dimensions
        }}

    }};
</script>

</html>


'''.format(text,height,height)
    return  render_template('template.html')



@app.route('/lists')
def print_list():
    return render_template('lists.html')

@app.route('/beta', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':

        # check if the post request has the file part

        if 'uploaded_image' not in request.files:

            return redirect(request.url)
        
        file = request.files['uploaded_image']
        test = request.form['uploaded_bb']
        
 

        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            print('2')
            return redirect(request.url)
        if file and allowed_file(file.filename) and test!='':


            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            filestr = file.read()
            
            
        
            result = []
            
            test = test.split('px')[:-1]
            image_left = float(test[0])
            image_top = float(test[1])
            image_width = float(test[2])
            image_height = float(test[3])
            
            re = []
            npimg = np.fromstring(filestr, np.uint8)
            image = cv2.imdecode(npimg, 1)
            height,width,channel = image.shape
            
            for t in range(4,len(test)):
                
                if t %4==0:
                    re.append(int((int(test[t])-int(image_left))*width/image_width))
                if t%4==1:
                    re.append(int((int(test[t])-int(image_top))*height/image_height))
                if t%4==2:
                    re.append(int(int(test[t])*width/image_width))         
                if t %4==3 :
                    re.append(int(int(test[t])*height/image_height))
                    result.append(re)
                    re=[]
                    continue
            urls=[]       
            urls=[]       
            npimg = np.fromstring(filestr, np.uint8)
            image = cv2.imdecode(npimg, 1)
            height,width,channel = image.shape
            for res in result:
                
                count = random.randint(0,100000000) 
                cor = res
                box_height = cor[3]
                box_width = cor[2]

                start_x = cor[0]
                start_y = cor[1]
                
                end_y = start_y+box_height
                
                end_x = start_x+box_width
                im = image[start_y:end_y,start_x:end_x]

                id_ = random.randint(0,10000000)
                img_str = cv2.imencode('.jpg', im)[1].tostring()

                blob = bucket.blob('face/{}.jpg'.format(id_))
                blob.upload_from_string(img_str,content_type='application/octet-stream')
                blob.make_public()
                url = blob.public_url
                urls.append(url)   

            face_list = []
            async def face(url):
                
                res = requests.get('https://animerecogres34.azurewebsites.net/api/recog?url={}'.format(url)).text

                return res

            async def network(urls):
                tasks = []
                for url in urls:
                    
                    task = asyncio.get_event_loop().create_task(face(url))
                    tasks.append(task)
                await asyncio.wait(tasks)
                for task in tasks:
                    face_list.append(task.result())
            #loop = asyncio.get_event_loop()
            
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(asyncio.ensure_future(network(urls)))
            
            text =''
            id_ =0
            count = 0
            height_1 = 0
            with db.connect() as conn:
                for face in face_list:
                    count +=1
                    text += '<div style="font-size: 300%;">Input</div>'
                    text = text+"<img src ={} height=300 width=300>".format(urls[id_])
                    id_ +=1
                    res = face.split("\n")
                    text += '<div style="font-size: 300%;">Output</div>'
                    for re in res[:-1]:
                        name = re.split(':')[0]
                        text += "<div>"

                        query = conn.execute(
                            "Select id from character_database where name='{}'".format(name)
                        ).fetchall()
                        if len(query)!=0:
                            query = query[0][0]
                        else:
                            continue
                        text += "<img src=https://storage.googleapis.com/animeprojectx.appspot.com/image_character/{}.jpg height=100 width=100> {} ".format(str(query).zfill(5),name)
                        
                        query = conn.execute(
                            "Select anime_id from character_database where name='{}'".format(name)
                        ).fetchall()
                        if len(query)!=0:
                            query = query[0][0]
                        else:
                            continue
                        anime_ids = query.split(',')
                        x = '<br>'
                        height_1 += len(anime_ids)
                        if len(anime_ids)>5:
                            anime_ids = anime_ids[:6]
                        for anime_id in anime_ids[:-1]:
                            
                            query = conn.execute(
                                "SELECT name,alt_name,eps,studio,year,season FROM anime_database where id = {}".format(anime_id)
                            ).fetchall()[0]
                            ##x = x+ "<a title ='alt name={} $$ eps={} $$ studio={} $$ year={} $$ season={}' href =''>{}</a> ".format(query[1],query[2],query[3],query[4],query[5],query[0])
                            x = x +'''
    <div class="anime"><a href="">{}</a>
        <div class="anime-info">Anime Detail
            <div class="card1" style="width: 12rem; ">
                <img class="card-img-top" src=https://storage.googleapis.com/animeprojectx.appspot.com/anime_image/{}.jpg alt="Card image cap">

                <ul class="list-group list-group-flush">
                    <li class="list-group-item">Alt Name: {}</li>
                    <li class="list-group-item">Eps: {}</li>
                    <li class="list-group-item">Studio: {}</li>
                    <li class="list-group-item">Year: {}</li>
                    <li class="list-group-item">Season: {}</li>
                </ul>
            </div>
        </div>
    </div>
                            '''.format(query[0],str(anime_id).zfill(5),query[1],query[2],query[3],query[4],query[5])
                            x += '<br>'
                        text += "{}</div>".format(x)
            height = 300+ 1000*count+height_1*17
            return '''
<!doctype html>
<html lang="en">

<head>
    <title>Project Anime X</title>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

    <!-- Bootstrap CSS -->
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
</head>

<body>
    <!-- HEADER START-->
    <header id="header">
        <div class="content">
            <div id="logo"><a href="#home">NON-OTAKU GROUP </a></div>
            <nav id="nav">
                <ul id="slidenav">
                    <li><a href="#home" class="active" title="Oxana Web">Home</a></li>
                    <li><a href="#about" title="About">Search</a></li>
                    <li><a href="#services" title="Services">Tutorial</a></li>
                    
                    <li><a href="#contact" title="Contact">Contact</a></li>
                </ul>
                <ul id="slidenavdesktop">
                    <li><a href="#home" class="active" title="Next Section">Home</a></li>
                    <li><a href="#about" title="Next Section">Search</a></li>
                    <li><a href="#services" title="Next Section">Tutorial</a></li>
                    
                    <li><a href="#contact" title="Next Section">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>
    <!-- SLIDES START -->
    <div id="home">
        <div class="content">
            <h1><strong>ANIME FINDER</strong></h1>
            <b>Finding any Anime Characters by Images</b>
            <br/>
            <br/>
            <img src="https://storage.googleapis.com/animeprojectx.appspot.com/rem.jfif" alt="Smiley face" width="165" >
            <div id="divider"> </div>

            <a href="#about">
                <div id="button">
                    <h3>START</h3>
                </div>
            </a>
            <div id="arrow"></div>
        </div>
    </div>
    <div id="about">
        <div class="uploadArea">
            <div class="col-md-8">
                <h4 class="mb-3">Upload Image</h4>
                <form method="POST" enctype="multipart/form-data">
                    <div class="col-md-6 md-3">
                        <input type="file" name="uploaded_image" accept="image/*" onchange="loadFile(event)">
                        <div><small class="text-muted">Accepted mime-type: image/jpeg, image/png</small></div>
                    </div>
                    
                    <button class="btn btn-primary btn-lg btn-block" type="submit">Upload</button>
                </form>
            </div>
            <img id="img">
        </div>
        {}
    </div>
    <div id="services">
        <div class="content">
            <div class="quotes_container">
                <p class="quotes">Ứng dụng hỗ trợ tìm kiếm các nhân vật anime thông qua khuôn mặt.</p>
                <p class="quotes">Ấn nút <b class = "redtext">Chọn tệp</b>, chọn ảnh rồi bấm <b class = "redtext">Upload</b>. Đợi 40s đến 1p là web sẽ trả về top 5 nhân vật gần giống nhất kèm thêm 1 số thông tin của nhân vật.</p>
                
                <p class="quotes">Hiện tại ứng dụng có thể nhận diện khoảng 550 nhân vật của các bộ trong <a href="https://animeprojectx.appspot.com/lists" class = "redtext"><u>danh sách</u></a> với độ chính xác là 98% (trong điều kiện tốt nhất), ảnh có một hoặc nhiều nhân vật đều dùng được. </p>
                <p class="quotes">Bên cạnh các ảnh chứa các nhân vật trong anime, ứng dụng cũng có thể nhận diện nhân vật thông qua fan art, figure, cosplay,... nhưng với độ chính xác thấp hơn. </p>
                <p class="quotes">Hướng dẫn sử dụng <a href="https://animeprojectx.appspot.com/beta" class = "redtext"><u>phiên bản beta</u></a>: </p>
                <p class="quotes">- Phiên bản beta giúp dùng người dùng tạo khung chứa khuôn mặt rồi upload. Nhờ vậy mà độ chính xác tăng đáng kể và thời gian xuống khoảng 20s. Nhưng do dùng hơi bất tiện nên có tên là beta :v. </p>
                <p class="quotes">- Ấn nút <b class = "redtext">Chọn tệp</b>, rồi chọn ảnh. Sau đó ảnh sẽ hiện lên trên trình duyệt. Người dùng click vào ảnh để tạo các khung chứa khuôn mặt cần nhận diện(có thể 1 hoặc nhiều khung) rồi ấn <b class = "redtext">Upload</b>. </p>
                <p class="quotes">- Nếu muốn dùng tiếp thì người dùng phải <b class = "redtext">reload</b> lại trang. </p>
                
            </div>
        </div>
    </div>

    <div id="contact">
        <div class="content">
            <div class="contact_container">


                
                <div id="social">
                    <a class="facebookBtn smGlobalBtn" href="https://www.facebook.com/thegiang.phan"></a>

                </div>

            </div>
            
        </div>
    </div>
    <!-- SLIDES END -->
</body>
<!-- Optional JavaScript -->
<!-- jQuery first, then Popper.js, then Bootstrap JS -->
<script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
<script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>

<link rel="stylesheet" type="text/css" href="/static/style_x.css">
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>


<script>
        document.getElementById("about").style.height = {} + "px";
        var loadFile = function(event) {{
        var output = document.getElementById('img');
        output.src = URL.createObjectURL(event.target.files[0]);
        var img = new Image();
        img.src = output.src;
        img.onload = function() {{
            var height = img.height;
            var width = img.width;


            document.getElementById("about").style.height = height + {} + "px";
            // code here to use the dimensions
        }}

    }};
</script>

</html>


'''.format(text,height,height)
    return  render_template('beta.html')

if __name__ == '__main__':
    count = 0
    app.run(host='0.0.0.0', port=5000, debug=True)
