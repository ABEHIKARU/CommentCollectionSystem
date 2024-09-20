
// データベースを開く関数
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("TranslationAnalysisDB", 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            // オブジェクトストアを作成
            if (!db.objectStoreNames.contains("AnalysisData")) {
                const objectStore = db.createObjectStore("AnalysisData", { keyPath: "id", autoIncrement: true });

                // 各フィールドのインデックス作成
                objectStore.createIndex("original", "original", { unique: false });
                objectStore.createIndex("summary", "summary", { unique: false });
                objectStore.createIndex("sentiment", "sentiment", { unique: false });
                objectStore.createIndex("date", "date", { unique: false });
            }
        };

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(`Database error: ${event.target.errorCode}`);
        };
    });
}

// データをIndexedDBに保存する関数
function saveDataToIndexedDB(db, data) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(["AnalysisData"], "readwrite");
        const store = transaction.objectStore("AnalysisData");

        // データを追加
        store.add(data);

        transaction.oncomplete = () => {
            resolve("Data saved successfully!");
        };

        transaction.onerror = (event) => {
            const errorMessage = `DBにデータを追加できませんでした。`;
            
            // エラーメッセージを表示する関数を呼び出し
            displayErrorMessage(errorMessage);
        
            reject(errorMessage);
        };
    });
}

// atフィールドをdateに変換する関数
function convertReviewData(review) {
    return {
        date: review.at,  // atをdateにマッピング
        sentiment: review.sentiment,
        summary: review.summary,
        original: review.content // contentをoriginalにマッピング
    };
}

// IndexedDBからすべてのデータを取得する関数
function getAllDataFromIndexedDB(db) {
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(["AnalysisData"], "readonly");
        const store = transaction.objectStore("AnalysisData");

        const request = store.getAll();

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(`Transaction error: ${event.target.errorCode}`);
        };
    });
}


// IndexedDBにレビューを保存し、その後すべてのデータを読み込んで console.logに表示
openDatabase()
    .then(db => {
        // すべてのレビューを保存
        reviews.forEach(review => {
            const convertedReview = convertReviewData(review);  // フィールド名を変換
            saveDataToIndexedDB(db, convertedReview)
                .then(message => console.log(message))
                .catch(error => console.error(error));
        });

        // 保存されたデータを取得して表示
        getAllDataFromIndexedDB(db)
            .then(data => {
                console.log("IndexedDB内のデータ: ", data);  // ここで保存されたデータを確認
            })
            .catch(error => console.error(error));
    })
    .catch(error => console.error("Database error:", error));
    
function displayErrorMessage(message) {
    // エラーメッセージを表示するHTML要素を取得
    const errorMessageDiv = document.getElementById('errorMessage');

    // エラーメッセージを設定
    errorMessageDiv.textContent = message;

    // エラーメッセージを赤色に
    errorMessageDiv.style.color = 'red';
}


// IndexedDBから20件データを取得して表示する関数
// function displayReviews() {
//     openDatabase()  // IndexedDBデータベースを開く
//         .then(db => {
//             getAllDataFromIndexedDB(db)  // データベースからすべてのデータを取得
//                 .then(data => {
//                     const reviewTable = document.querySelector('#review-table tbody'); // 表のtbody要素を取得
//                     let displayCount = Math.min(data.length, 20); // 20件以上なら20件まで表示、20件未満なら全件表示

//                     // データが存在するかチェック
//                     if (displayCount > 0) {
//                         // 既存の表にデータを追加
//                         data.slice(0, displayCount).forEach((review, index) => {
//                             const row = reviewTable.insertRow(); // 新しい行を作成
                            
//                             // 各セルを作成してデータを挿入
//                             let cellNo = row.insertCell(0);    
//                             let cellDate = row.insertCell(1);    
//                             let cellSentiment = row.insertCell(2); 
//                             let cellSummary = row.insertCell(3);   
//                             let cellOriginal = row.insertCell(4);  

//                             // 各セルに対応するデータをセット
//                             cellNo.textContent = index + 1;           // レビューの番号を設定
//                             cellDate.textContent = review.date;        // 投稿日時（dateフィールド）を表示
//                             cellSentiment.textContent = review.sentiment; // + / - の評価を表示
//                             cellSummary.textContent = review.summary;   // 要約（summaryフィールド）を表示
//                             cellOriginal.textContent = review.original; // 原文（originalフィールド）を表示

//                             // 種別セルの背景色を条件に応じて設定（RGBAで透明度を加える）
//                             if (review.sentiment === '+') {
//                                 cellSentiment.style.backgroundColor = 'rgba(0, 0, 255, 0.2)'; // 薄い青
//                             } else if (review.sentiment === '-') {
//                                 cellSentiment.style.backgroundColor = 'rgba(255, 0, 0, 0.2)'; // 薄い赤
//                             } else if (review.sentiment === '~') {
//                                 cellSentiment.style.backgroundColor = 'rgba(0, 255, 0, 0.2)'; // 薄い緑
//                             }
//                         });
//                     } else {
//                         // データが無い場合はメッセージ表示
//                         const errorMessageDiv = document.getElementById('errorMessage');  // エラーメッセージ表示用のdivを取得
//                         errorMessageDiv.textContent = '表示するレビューがありません。';  // エラーメッセージを設定
//                     }
//                 })
//                 .catch(error => console.error("データ取得エラー: ", error));  // データ取得エラー時の処理
//         })
//         .catch(error => console.error("Database error:", error));  // データベースエラー時の処理
// }

let currentPage = 1;  // 現在のページ番号
const itemsPerPage = 20;  // 1ページに表示するレビューの件数

// IndexedDBからデータを取得し、ページごとに表示
function displayReviews() {
    openDatabase()
        .then(db => {
            getAllDataFromIndexedDB(db)
                .then(data => {
                    const reviewTable = document.querySelector('#review-table tbody');  // 表のtbody要素を取得
                    reviewTable.innerHTML = '';  // 表の内容をクリア
                    const totalReviews = data.length;  // 全体のレビュー件数
                    const totalPages = Math.ceil(totalReviews / itemsPerPage);  // 全ページ数を計算

                    // 表示するレビューの開始と終了インデックスを計算
                    const start = (currentPage - 1) * itemsPerPage;
                    const end = Math.min(start + itemsPerPage, totalReviews);  // 残りのデータが少ない場合は最後まで表示
                    const reviewsToDisplay = data.slice(start, end);  // 現在のページのレビューを取得

                    // レビューを表に追加
                    reviewsToDisplay.forEach((review, index) => {
                        const row = reviewTable.insertRow();
                        let cellNo = row.insertCell(0);
                        let cellDate = row.insertCell(1);
                        let cellSentiment = row.insertCell(2);
                        let cellSummary = row.insertCell(3);
                        let cellOriginal = row.insertCell(4);

                        cellNo.textContent = start + index + 1;  // 正しい番号を設定
                        cellDate.textContent = review.date;
                        cellSentiment.textContent = review.sentiment;
                        cellSummary.textContent = review.summary;
                        cellOriginal.textContent = review.original;

                        // 背景色設定
                        if (review.sentiment === '+') {
                            cellSentiment.style.backgroundColor = 'rgba(0, 0, 255, 0.2)';
                        } else if (review.sentiment === '-') {
                            cellSentiment.style.backgroundColor = 'rgba(255, 0, 0, 0.2)';
                        } else if (review.sentiment === '~') {
                            cellSentiment.style.backgroundColor = 'rgba(0, 255, 0, 0.2)';
                        }
                    });

                     // ページ番号を更新
                     const currentPageDisplay = document.getElementById('currentPageDisplay');
                     currentPageDisplay.textContent = `${currentPage}ページ目`;

                    // 「次へ」ボタンの表示・非表示を制御
                    const nextPageButton = document.querySelector(".nextpageButton");
                    if (totalReviews > end) {
                        nextPageButton.style.display = 'inline';  // まだ次のページがある場合は表示
                    } else {
                        nextPageButton.style.display = 'none';  // これ以上のデータがない場合は非表示
                    }

                    // 「前へ」ボタンの表示・非表示を制御
                    const backPageButton = document.querySelector(".backpageButton");
                    if (currentPage > 1) {
                        backPageButton.style.display = 'inline';  // 1ページ目以外は表示
                    } else {
                        backPageButton.style.display = 'none';  // 1ページ目の場合は非表示
                    }
                })
                .catch(error => console.error("データ取得エラー: ", error));
        })
        .catch(error => console.error("Database error:", error));
}

document.addEventListener("DOMContentLoaded", function () {

    // beforeunload イベントリスナー
    var onBeforeunloadHandler = function(e) {
        e.preventDefault();
        e.returnValue = '';
    };

    // beforeunload イベントを追加
    window.addEventListener("beforeunload", onBeforeunloadHandler, false);

    const formBtns = document.querySelectorAll(".backpageButton,.nextpageButton,#backToSearchSubmit");

    formBtns.forEach(function (formBtn) {
        formBtn.addEventListener("click", function () {
            // 特定の操作（ページ遷移）時には確認ダイアログを出さない
            window.removeEventListener("beforeunload", onBeforeunloadHandler);
        });
    });
});

// 「次へ」ボタンのクリックイベントハンドラ
document.querySelector(".nextpageButton").addEventListener("click", function (event) {
    event.preventDefault();  // デフォルトのフォーム動作を防ぐ
    currentPage++;  // ページを進める
    displayReviews();  // 次のページのレビューを表示
});

// 「前へ」ボタンのクリックイベントハンドラ
document.querySelector(".backpageButton").addEventListener("click", function (event) {
    event.preventDefault();  // デフォルトのフォーム動作を防ぐ
    if (currentPage > 1) {
        currentPage--;  // ページを戻す
        displayReviews();  // 前のページのレビューを表示
    }
});

// // ページ読み込み時にレビューを表示
// document.addEventListener("DOMContentLoaded", function () {
//     displayReviews();  // 初回読み込み時にレビューを表示
// });