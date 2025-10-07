const msg1 = document.getElementById("message");
const msg2 = document.getElementById("message2");

msg1.textContent = "JavaScriptで変更した pタグ1";
msg2.textContent = "JavaScriptで変更した pタグ2";

const p = document.createElement("p");  // 紙を新しく作る
p.textContent = "JavaScriptで作成した pタグ";
document.body.appendChild(p);           // 教室の壁に貼る