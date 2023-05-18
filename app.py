from flask import Flask,render_template,request,jsonify,send_file,make_response
from gridfs import GridFS
from pymongo import MongoClient

# mongodb objectID용
from bson import ObjectId

# 이미지
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

# 이미지 담을 경로
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# mongo db 연결하기
from pymongo import MongoClient

client = MongoClient("mongodb+srv://sparta:test@cluster0.k23feze.mongodb.net/?retryWrites=true&w=majority") # mongo url입력
db = client["team"]





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
    try: 
        name_receive = request.form["name_give"]
        address_receive = request.form["address_give"]
        hobby_receive = request.form["hobby_give"]
        advantage_receive = request.form["advantage_give"]
        work_style_receive = request.form["work_style_give"]
        comment_receive = request.form["comment_give"]
        blog_receive = request.form["blog_give"]
        img_file = request.files["img_give"]

        filename = secure_filename(img_file.filename) # 파일 이름 다듬기
        img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # 업로드 폴더에 저장!

        doc = {
            "name": name_receive,
            "address": address_receive,
            "hobby": hobby_receive,
            "advantage": advantage_receive,
            "work_style": work_style_receive,
            "comment": comment_receive,
            "blog": blog_receive,
            "img": filename  # 이미지 파일명 저장
        } 
        
        db.members.insert_one(doc)

        return jsonify({"msg": "팀원 등록 완료"}), 201

    except Exception as err:
        error_message = str(err)
        return jsonify({"msg": f"팀원 등록 실패: {error_message}"}), 500
    
           
# 팀원db : 팀원 데이터 가져오기
@app.route("/members", methods=["GET"])
def member_get():
    try:
        all_members = list(db.members.find({}))

        for member in all_members:
            
            # _id 필드의 ObjectId 값을 문자열로 변환하여 가져오기 !!!
            member["_id"] = str(member["_id"])
            
             # 이미지 경로 가져오기
            image_filename = member.get("img")
            
            if image_filename:
                member["img"] = f"/uploads/{image_filename}"  # 이미지 경로 설정
            
                        
        return jsonify({"result": all_members}), 200
    
    except Exception as err:
        return jsonify({"msg": "팀원 데이터 Fetch 에러"}), 500

# 팀원db: 팀원 데이터 수정하기
@app.route("/members/<member_id>", methods=["PUT"])
def member_edit(member_id):
    try:
        update_data = request.form.to_dict()

        # 이미지 관련 코드
        img_file = request.files["img"]
        filename = secure_filename(img_file.filename) # 파일 이름 다듬기
        img_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) 

        update_data["img"] = filename  # 이미지 파일명 저장

        # 기존 이미지 파일 삭제
        member = db.members.find_one({"_id": ObjectId(member_id)})
        old_filename = member.get("img")
        if old_filename:
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)

        db.members.update_one({"_id": ObjectId(member_id)}, {"$set": update_data})

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
    # app.run("0.0.0.0", port=5000, debug=True)
    app.run()