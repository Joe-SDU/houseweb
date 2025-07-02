from flask import Flask, request, render_template, jsonify, send_from_directory
import os
import uuid
import json

app = Flask(__name__)

# 获取当前脚本所在目录的绝对路径
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 设置上传文件夹为项目目录中的 houses 文件夹
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'houses')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"创建上传目录: {UPLOAD_FOLDER}")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_house', methods=['GET', 'POST'])
def add_house():
    if request.method == 'POST':
        address = request.form.get('address')
        rent = request.form.get('rent')
        water_fee = request.form.get('water_fee')
        electricity_fee = request.form.get('electricity_fee')

        if not address or not rent or not water_fee or not electricity_fee:
            return jsonify({"error": "必填字段未填写"}), 400

        try:
            distance = float(request.form.get('distance', 0))
            agency_fee = float(request.form.get('agency_fee', 0))
            depreciation = float(request.form.get('depreciation', 0))
            rent = float(rent)
            water_fee = float(water_fee)
            electricity_fee = float(electricity_fee)
        except ValueError:
            return jsonify({"error": "数字字段输入无效，请输入有效的浮点数"}), 400

        payment_method = request.form.get('payment_method', '')
        note = request.form.get('note', '')

        upload_id = str(uuid.uuid4())
        upload_dir = os.path.join(app.config['UPLOAD_FOLDER'], upload_id)
        os.makedirs(upload_dir)

        budget = agency_fee + rent + 100 + depreciation
        budget = round(budget, 2)

        house_info = {
            "address": address,
            "distance": distance,
            "rent": rent,
            "agency_fee": agency_fee,
            "water_fee": water_fee,
            "electricity_fee": electricity_fee,
            "depreciation": depreciation,
            "payment_method": payment_method,
            "note": note,
            "budget": budget
        }

        if 'images' in request.files:
            images = request.files.getlist('images')
            for image in images:
                if image.filename:
                    image.save(os.path.join(upload_dir, image.filename))

        with open(os.path.join(upload_dir, 'info.json'), 'w') as f:
            json.dump(house_info, f)

        return jsonify({"message": "房屋信息保存成功", "upload_id": upload_id}), 200
    return render_template('add_house.html')


@app.route('/view_houses')
def view_houses():
    houses = []
    try:
        for house_id in os.listdir(app.config['UPLOAD_FOLDER']):
            house_dir = os.path.join(app.config['UPLOAD_FOLDER'], house_id)
            if os.path.isdir(house_dir):
                info_path = os.path.join(house_dir, 'info.json')
                if os.path.exists(info_path):
                    with open(info_path, 'r') as f:
                        info = json.load(f)
                    images = []
                    try:
                        for img in os.listdir(house_dir):
                            if img.lower().endswith(('.png', '.jpg', '.jpeg')) and img != 'info.json':
                                # 修复：使用 URL 路径格式而不是系统路径
                                images.append(f"{house_id}/{img}")
                    except Exception as e:
                        print(f"读取图片列表出错: {e}")
                    houses.append({
                        "id": house_id,
                        "address": info["address"],
                        "budget": info["budget"],
                        "images": images
                    })
    except Exception as e:
        print(f"查看房屋信息出错: {e}")
    return render_template('view_houses.html', houses=houses, total=len(houses))

@app.route('/view_house/<house_id>')
def view_house(house_id):
    house_dir = os.path.join(app.config['UPLOAD_FOLDER'], house_id)
    if os.path.isdir(house_dir):
        info_path = os.path.join(house_dir, 'info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
            # 修复：使用正确的路径格式
            images = [f"{house_id}/{img}" for img in os.listdir(house_dir) 
                     if img.lower().endswith(('.png', '.jpg', '.jpeg')) and img != 'info.json']
            info['images'] = images
            return render_template('house_detail.html', house=info)
    return "房屋信息不存在", 404


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    if request.method == 'POST':
        ac_type = request.form.get('ac_type')
        input_power = request.form.get('input_power')
        cooling_season_power = request.form.get('cooling_season_power')
        electricity_price = request.form.get('electricity_price')

        if not electricity_price:
            return jsonify({"error": "每小时电费为必填字段"}), 400

        if ac_type == '定频' and not input_power:
            return jsonify({"error": "定频空调需要输入输入功率"}), 400
        elif ac_type == '变频' and not cooling_season_power:
            return jsonify({"error": "变频空调需要输入制冷季耗电量"}), 400

        try:
            if ac_type == '定频':
                hourly_power = float(input_power) / 1000
                hourly_cost = hourly_power * float(electricity_price)
                result_msg = f"每小时电费为：{hourly_cost} 元，每小时电度数: {hourly_power} 度"
            else:
                hourly_power = float(cooling_season_power) / 1136
                hourly_cost = hourly_power * float(electricity_price)
                result_msg = f"每小时电费为：{hourly_cost} 元，每小时电度数: {hourly_power} 度"

            hourly_power = round(hourly_power, 2)
            hourly_cost = round(hourly_cost, 2)

            return jsonify({"result": result_msg}), 200
        except ValueError:
            return jsonify({"error": "数字字段输入无效，请输入有效的浮点数"}), 400

    return render_template('calculator.html')


@app.route('/houses/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    # 只在开发环境运行
    if os.getenv('RENDER'):  # 检测是否在Render环境
        app.run(host='0.0.0.0', port=10000, debug=False)
    else:
        app.run(debug=True)
