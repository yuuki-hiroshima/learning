// テーブル要素
const tbody = document.querySelector("#result tbody");

// 表示クリア
function clearTable() {
  tbody.innerHTML = "";
}

// 行を1件追加
function addRow({ id, name, email }) {
  const tr = document.createElement("tr");
  tr.innerHTML = `<td>${id}</td><td>${name}</td><td>${email}</td>`;
  tbody.appendChild(tr);
}

// APIから取得して表に描画
async function fetchAndRender(url) {
  clearTable();
  try {
    const res = await fetch(url, { headers: { "Accept": "application/json" } });
    if (!res.ok) {
      alert(`エラー: HTTP ${res.status}`);
      return;
    }
    const data = await res.json(); // ここで配列に変換
    data.forEach(addRow);
  } catch (e) {
    alert("通信エラー: " + (e?.message || e));
  }
}

// ボタン紐付け（URLだけ切り替え）
document.getElementById("btn1").addEventListener("click", () => fetchAndRender("/api/list"));
document.getElementById("btn2").addEventListener("click", () => fetchAndRender("/api/list?q=太郎"));
document.getElementById("btn3").addEventListener("click", () => fetchAndRender("/api/list?sort=email_asc"));