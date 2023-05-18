from flask import Flask,render_template,request,jsonify,send_file,make_response
from gridfs import GridFS
from pymongo import MongoClient

# 이미지 데이터 변환때문에 넣음
from io import BytesIO
import base64
import io

# mongodb objectID용
from bson import ObjectId

app = Flask(__name__)

# mongo db 연결하기
from pymongo import MongoClient

client = MongoClient("mongodb+srv://sparta:test@cluster0.k23feze.mongodb.net/?retryWrites=true&w=majority") # mongo url입력
db = client["team"]

# def : 이미지 확장자 제한하기
ALLOWED_EXTENSIONS = {"png"}
def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# route : home화면
@app.route("/")
def home():
    return render_template("index.html")

# route : 팀원 페이지 이동
@app.route("/members/<member_id>")
def setPage(member_id):
    member = db.members.find_one({"_id": ObjectId(member_id)})  # DB에서 해당 팀원 데이터를 가져옴

    if member:
        name = member.get("name")
        # print(name) 

        if name == "유지은":
            return render_template("ug.html", member=member)
        elif name == "김진경":
            return render_template("kim.html", member=member)
        elif name == "최원빈":
            return render_template("choi.html", member=member)
        elif name == "박예찬":
            return render_template("park.html", member=member)
        elif name == "이예진":
            return render_template("lee.html", member=member)

    return render_template("ug.html", member=member)

# 팀원db : 팀원 데이터 생성
@app.route("/members", methods=["POST"])
def member_post():
    name_receive = request.form["name_give"]
    address_receive = request.form["address_give"]
    hobby_receive = request.form["hobby_give"]
    advantage_receive = request.form["advantage_give"]
    work_style_receive = request.form["work_style_give"]
    comment_receive = request.form["comment_give"]
    blog_receive = request.form["blog_give"]
    img_file = request.files["img_give"]
    
    if img_file and allowed_file(img_file.filename): #이미지 확장자 확인 함수로 png로 들어왔는지 체크
        image_binary = img_file.read()  # 이미지 파일을 바이너리로 읽어옴
        encoded_image = base64.b64encode(image_binary).decode("utf-8")  # 이미지 데이터를 Base64로 인코딩
            
        doc = {
            "name": name_receive,
            "address": address_receive,
            "hobby": hobby_receive,
            "advantage": advantage_receive,
            "work_style": work_style_receive,
            "comment": comment_receive,
            "blog": blog_receive,
            "img": encoded_image  # Base64로 인코딩된 이미지 데이터 저장
        } 
        db.members.insert_one(doc)
                 
        return jsonify({"msg": "팀원 등록 완료"}), 201
    else:
        if img_file is None or not allowed_file(img_file.filename):
            return jsonify({"msg": ".png 형식의 이미지를 넣어주세요!"}), 400
        else:
            return jsonify({"msg": "팀원 등록 실패"}), 500
           
# 팀원db : 팀원 데이터 가져오기
@app.route("/members", methods=["GET"])
def member_get():
    try:
        all_members = list(db.members.find({}))

        for member in all_members:
            
            # _id 필드의 ObjectId 값을 문자열로 변환하여 가져오기 !!!
            member["_id"] = str(member["_id"])
            
            # 이미지 가져오기
            image_data = member.get("img", None)
            if image_data:
                member["img"] = image_data
                        
        return jsonify({"result": all_members}), 200
    
    except Exception as err:
        return jsonify({"msg": "팀원 데이터 Fetch 에러"}), 500

# route : 바이너리 형식 이미지 파일 변환 후 저장하기
@app.route("/members/<member_id>/image")
def get_image(member_id):
    try:
        member = db.members.find_one({"_id": ObjectId(member_id)}, {"img": True})

        if not member or "img" not in member:
            return "이미지를 찾을 수 없음", 404

        image_data = member["img"]
        padding = len(image_data) % 4
        image_data += "=" * padding
        image_bytes = base64.b64decode(image_data.encode("utf-8"))

        image = io.BytesIO(image_bytes)
        image.seek(0)

        return send_file(
            image,
            mimetype="image/png",
            as_attachment=False
        )
        
    except Exception as err:
        return "서버 오류", 500

# 팀원db : 팀원 데이터 수정하기
@app.route("/members/<member_id>", methods=["PUT"])
def member_edit(member_id):
    try:
        update_data = request.form.to_dict()
        
        if "img" in request.files and allowed_file(request.files["img"].filename):
            img_file = request.files["img"]
            image_binary = img_file.read()
            encoded_image = base64.b64encode(image_binary).decode("utf-8")
            update_data["img"] = encoded_image
        
        db.members.update_one({"_id": ObjectId(member_id)}, {"$set": update_data})
        
        # print(update_data)
        
        return jsonify({"message": f"{member_id}번 팀원 수정 성공"}), 200

    except Exception as err:
        return jsonify({"message": f"{member_id}번 팀원 수정 실패"}), 500

# 팀원db : 팀원 데이터 삭제하기
@app.route("/members/<member_id>", methods=["DELETE"])
def member_delete(member_id):
    try:
        db.members.delete_one({"_id": ObjectId(member_id)})
        return jsonify({"message": f"{member_id}번 팀원 삭제 성공"}), 204

    except Exception as err:
        return jsonify({"message": f"{member_id}번 팀원 삭제 실패"}), 500

# 방명록db - 방명록 데이터 생성
@app.route("/comments", methods=["POST"])
def comments_post():
    try:
        name_receive = request.form["name_give"]
        comment_receive = request.form["comment_give"]
        member_id_receive = request.form["member_id_give"]
        doc = {
            "name":name_receive,
            "comment":comment_receive,
            "member_id":member_id_receive
        }
        db.comments.insert_one(doc)
        
        return jsonify({"msg": "방명록 등록 완료"}), 201
    
    except Exception as err:
        return jsonify({"msg": "방명록 저장 실패"}), 500

# 방명록db - 방명록 데이터 가져오기
@app.route("/comments/<member_id>", methods=["GET"])
def comments_get(member_id):
    try:
        all_comment = list(db.comments.find({"member_id": member_id}))
        
        for comment in all_comment:
            
            # _id 필드의 ObjectId 값을 문자열로 변환하여 가져오기 !!!
            comment["_id"] = str(comment["_id"])
            
        return jsonify({"result": all_comment})
    
    except Exception as err:
        return jsonify({"ms": "방명록 데이터 Fetch 에러"})
        
# 방명록db - 방명록 수정
@app.route("/comments/<comment_id>", methods=["PUT"])
def comment_edit(comment_id):
    try:
        update_data = request.get_json()
        comment = update_data["comment"]
        
        db.comments.update_one({"_id": ObjectId(comment_id)}, {"$set": {"comment": comment}})
        
        return jsonify({"message": f"{comment_id} 방명록 수정 완료"}), 200

    except Exception as err:
        return jsonify({"msg": f"{comment_id} 방명록 등록 실패"}), 500
      
# 방명록db - 방명록 삭제하기
@app.route("/comments/<comment_id>",methods=["DELETE"])
def comments_delete(comment_id):
    try:
        db.comments.delete_one({"_id": ObjectId(comment_id)})
        
        return jsonify({"message": f"{comment_id} 방명록 삭제 완료"}),200

    except Exception as err:
        return jsonify({"msg": f"{comment_id} 방명록 등록 실패"}), 500

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)