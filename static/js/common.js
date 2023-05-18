console.log('연결완료!')

//// 현재 URL 멤버 objectid 가져오기
const url = new URL(window.location.href);
const pathValue = url.pathname.split("/members/")[1];
// console.log(pathValue)

// GET : 멤버 데이터 불러오기
async function getMember() {
    try {
        const response = await fetch("/members", { method: "GET" });
        const resultData = await response.json();

        console.log(resultData);
        return resultData.result;
    } catch (error) {
        throw error;
    }
}

getMember()
    .then((members) => {
        members.forEach((member) => {
            ///// nav에 멤버 추가하기
            // console.log(member)
            const navList = document.querySelector(".nav-list");
            if (pathValue === member._id) {
                html_temp = `
                <li>
                    <a href="/members/${member._id}" class="btn btn-primary">${member.name}</a>
                </li>`
            } else {
                html_temp = `
                <li>
                    <a href="/members/${member._id}" class="btn btn-outline-primary">${member.name}</a>
                </li >
                    `;
            }
            navList.innerHTML += html_temp;


            //// 본문에 멤버 정보 뿌리기
            const memberWrap = document.querySelector(".my-info");
            let member_html_temp = ``;

            if (member._id === pathValue) {
                const imgURL = `${url}/image`;
                console.log(imgURL);
                member_html_temp = `
                                <div class="main-img-wrap">
                                    <img src="${imgURL}" alt="" />
                                </div>
                                <div class="info-text">
                                    <h2 class="name">${member.name}</h2>
                                    <p class="address"><span class="info-title">사는 곳 : </span>${member.address}</p>
                                    <p class="hobby"><span class="info-title">취미 : </span>${member.hobby}</p>
                                    <p class="advantage"><span class="info-title">장점 : </span>${member.advantage}</p>
                                    <p class="work_style"><span class="info-title">협업스타일 : </span>${member.work_style}</p>
                                    <p class="comment"><span class="info-title">다짐 한마디 : </span>${member.comment}</p>
                                    <p class="blog"><span class="info-title">블로그 주소 : </span>${member.blog}</p>
                                </div>
                           `;
                memberWrap.innerHTML += member_html_temp;
            }
        });
    })
    .catch((error) => {
        console.error(error);
    });


// POST : 멤버 데이터 전달하기
async function saveMember() {
    const memberName = document.querySelector("#memberName").value;
    const memberAddress = document.querySelector("#memberAddress").value;;
    const memberHobby = document.querySelector("#memberHobby").value;
    const memberAdvantage = document.querySelector("#memberAdvantage").value;
    const memberWorkStyle = document.querySelector("#memberWorkStyle").value;
    const memberComment = document.querySelector("#memberComment").value;
    const memberBlog = document.querySelector("#memberBlog").value;
    const memberImg = document.querySelector("#memberImg").files[0];
    // console.log(memberImg);

    const formData = new FormData();
    formData.append("name_give", memberName);
    formData.append("address_give", memberAddress);
    formData.append("hobby_give", memberHobby);
    formData.append("advantage_give", memberAdvantage);
    formData.append("work_style_give", memberWorkStyle);
    formData.append("comment_give", memberComment);
    formData.append("blog_give", memberBlog);
    formData.append("img_give", memberImg);

    try {
        const response = await fetch("/members", { method: "POST", body: formData });

        if (!response.ok) {
            const data = await response.json();
            const errorMessage = data.msg;

            alert(errorMessage);

            throw new Error(errorMessage);
        }

        alert('멤버 등록완료!');
        window.location.reload();

    } catch (error) {
        alert(error.message);
    }
}

// PUT : 멤버 데이터 수정 모달에 불러오기
let memberNameEdit = document.querySelector("#memberNameEdit");
let memberAddressEdit = document.querySelector("#memberAddressEdit");
let memberHobbyEdit = document.querySelector("#memberHobbyEdit");
let memberAdvantageEdit = document.querySelector("#memberAdvantageEdit");
let memberWorkStyleEdit = document.querySelector("#memberWorkStyleEdit");
let memberCommentEdit = document.querySelector("#memberCommentEdit");
let memberBlogEdit = document.querySelector("#memberBlogEdit");
let memberImg = document.querySelector("#memberImgEdit")

const btnEdit = document.querySelector('#btnEdit');
if (btnEdit !== null) {
    btnEdit.addEventListener('click', () => {

        try {
            fetch("/members", { method: "GET" })
                .then((response) => response.json())
                .then((responseData) => {
                    const members = responseData.result;

                    members.forEach((member) => {
                        if (member._id === pathValue) {
                            memberNameEdit.value = member.name;
                            memberAddressEdit.value = member.address;
                            memberHobbyEdit.value = member.hobby;
                            memberAdvantageEdit.value = member.advantage;
                            memberWorkStyleEdit.value = member.work_style;
                            memberCommentEdit.value = member.comment;
                            memberBlogEdit.value = member.blog;
                        }
                    });
                })
        } catch (error) {
            throw error;
        }
    })
}


// PUT : 멤버 수정 데이터 전달하기
function editComplete() {
    const formData = new FormData();
    formData.append("name", memberNameEdit.value);
    formData.append("address", memberAddressEdit.value);
    formData.append("hobby", memberHobbyEdit.value);
    formData.append("advantage", memberAdvantageEdit.value);
    formData.append("work_style", memberWorkStyleEdit.value);
    formData.append("comment", memberCommentEdit.value);
    formData.append("blog", memberBlogEdit.value);

    if (memberImgEdit !== null && memberImgEdit.files.length > 0) {
        formData.append("img", memberImgEdit.files[0]);
    }

    fetch(`/members/${pathValue}`, {
        method: "PUT",
        body: formData
    })
        .then(response => {
            if (response.ok) {
                alert('멤버 정보가 수정되었습니다!');
                window.location.reload();
            }
        })
        .catch(error => {
            console.error(error);
        });
}

// DELETE : 멤버 데이터 삭제하기
function deleteMember() {
    fetch(`/members/${pathValue}`, { method: "DELETE" })
        .then(response => {
            if (!response.ok) {
                throw new Error("멤버 삭제에 실패했습니다.");
            }
        })
        .then((members) => {
            alert('멤버가 삭제되었습니다!')
            window.location.href = "/";
        })
        .catch(error => {
            console.error(error);
        });
}

$(document).ready(function () {
    show_comment();
});

// POST : 방명록 저장하기
function save_comment() {
    let name = $('#name').val()
    let comment = $('#comment').val()
    let member_id = pathValue

    let formData = new FormData();
    formData.append("name_give", name);
    formData.append("comment_give", comment);
    formData.append("member_id_give", member_id);

    fetch('/comments', { method: "POST", body: formData, }).then((res) => res.json()).then((data) => {
        alert(data["msg"]);
        window.location.reload()
    });
}

// GET : 방명록 불러오기
function show_comment() {
    fetch(`/comments/${pathValue}`)
        .then((res) => res.json())
        .then((data) => {
            console.log(data)
            let rows = data['result']
            $('#comment-list').empty()
            rows.forEach((commentItem) => {
                let name = commentItem['name']
                let comment = commentItem['comment']
                let comment_id = commentItem['_id']

                let temp_html = `
                            <div class="card" data-commentID="${comment_id}">
                                <div class="card-body">
                                    <blockquote class="blockquote mb-3">
                                        </p>
                                        <p>${comment}</p>
                                        <footer class="blockquote-footer">${name}</footer>
                                    </blockquote>

                                    <div class="edit-wrap d-flex gap-1">
                                        <input type="text" id="commentEdit" class="form-control w-80 ">
                                        <button type="button" class="btn btn-success w-50" onClick="edit_comment(this)">수정!</button>
                                    </div>

                                    <div class="gstbuttons">
                                            <button type="button" id="commentEditBtn" class="btn btn-primary" onClick="editActive(this)">수정</button>  
                                            <button type="button" id="commentDeleteBtn" class="btn btn-secondary">삭제</button>
                                        </div>

                                </div>
                            </div>`
                $('#comment-list').append(temp_html)
            })
        })
}


// 방명록 수정하기 버튼 클릭시, 수정 인풋창 띄우기
function editActive(event) {
    // console.log(event)
    const thisCardElement = event.closest('.card');
    const editWrapElement = thisCardElement.querySelector('.edit-wrap');
    const blockquoteElement = thisCardElement.querySelector('.blockquote');
    const gstButtonsElement = thisCardElement.querySelector('.gstbuttons');

    editWrapElement.classList.add('active');
    blockquoteElement.classList.add('active');
    gstButtonsElement.classList.add('hide');
}

const commentEditBtn = document.getElementById('commentEditBtn');

if (commentEditBtn !== null) {
    commentEditBtn.addEventListener('click', editActive);
}



// PUT : 방명록 수정하기
function edit_comment(event) {
    const cardElement = event.closest('.card'); // 클릭한 버튼을 감싸는 card
    const commentId = cardElement.getAttribute('data-commentid'); // card commentid 데이터 값

    const commentEditInput = cardElement.querySelector("#commentEdit") // 수정내용 작성할 input 

    console.log(commentId)

    const update_data = {
        comment: commentEditInput.value
    };

    fetch(`/comments/${commentId}`, {
        method: "PUT",
        body: JSON.stringify(update_data),
        headers: {
            "Content-Type": "application/json"
        }
    })
        .then(response => {
            // console.log(response)
            if (response.ok) {
                alert('방명록이 수정되었습니다!');
                window.location.reload();
            }
        })
        .catch(error => {
            console.error(error);
        });
}

//DELETE : 방명록 삭제하기
document.addEventListener('click', function (event) {
    // 동적으로 생성된 button동작 위해서 이벤트 위임사용함!!!

    if (event.target.matches('#commentDeleteBtn')) {
        const cardElement = event.target.closest('.card'); // 버튼의 부모 card
        const commentId = cardElement.getAttribute('data-commentid'); // 버튼의 부모 card의 data-commentid값

        // console.log(commentId);

        fetch(`/comments/${commentId}`, {
            method: 'DELETE',
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('방명록 삭제에 실패했습니다.');
                }
                return response.json();
            })
            .then(() => {
                alert('방명록이 삭제되었습니다!');
                window.location.reload();
            })
            .catch(error => {
                console.error(error);
            });
    }
});

console.log("끝")