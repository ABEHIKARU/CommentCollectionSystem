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
function displayReviews() {
    openDatabase()  // IndexedDBデータベースを開く
        .then(db => {
            getAllDataFromIndexedDB(db)  // データベースからすべてのデータを取得
                .then(data => {
                    const reviewTable = document.querySelector('#review-table tbody'); // 表のtbody要素を取得
                    let displayCount = Math.min(data.length, 20); // 20件以上なら20件まで表示、20件未満なら全件表示

                    // データが存在するかチェック
                    if (displayCount > 0) {
                        // 既存の表にデータを追加
                        data.slice(0, displayCount).forEach((review, index) => {
                            const row = reviewTable.insertRow(); // 新しい行を作成
                            
                            // 各セルを作成してデータを挿入
                            let cellNo = row.insertCell(0);    
                            let cellDate = row.insertCell(1);    
                            let cellSentiment = row.insertCell(2); 
                            let cellSummary = row.insertCell(3);   
                            let cellOriginal = row.insertCell(4);  

                            // 各セルに対応するデータをセット
                            cellNo.textContent = index + 1;           // レビューの番号を設定
                            cellDate.textContent = review.date;        // 投稿日時（dateフィールド）を表示
                            cellSentiment.textContent = review.sentiment; // + / - の評価を表示
                            cellSummary.textContent = review.summary;   // 要約（summaryフィールド）を表示
                            cellOriginal.textContent = review.original; // 原文（originalフィールド）を表示

                            // 種別セルの色を条件に応じて設定
                            if (review.sentiment === '+') {
                                cellSentiment.style.color = 'blue'; // 種別が「+」の場合は青
                            } else if (review.sentiment === '-') {
                                cellSentiment.style.color = 'red';  // 種別が「-」の場合は赤
                            } else if (review.sentiment === '~') {
                                cellSentiment.style.color = 'green'; // 種別が「~」の場合は緑
                            }
                        });
                    } else {
                        // データが無い場合はメッセージ表示
                        const errorMessageDiv = document.getElementById('errorMessage');  // エラーメッセージ表示用のdivを取得
                        errorMessageDiv.textContent = '表示するレビューがありません。';  // エラーメッセージを設定
                    }
                })
                .catch(error => console.error("データ取得エラー: ", error));  // データ取得エラー時の処理
        })
        .catch(error => console.error("Database error:", error));  // データベースエラー時の処理
}


document.addEventListener("DOMContentLoaded", function () {
    // beforeunload イベントリスナー
    var onBeforeunloadHandler = function(e) {
        e.preventDefault();
        e.returnValue = '';
    };

    // beforeunload イベントを追加
    window.addEventListener('beforeunload', onBeforeunloadHandler, false);

    const formBtns = document.querySelectorAll(".backpageButton,.nextpageButton,#backToSearchSubmit");

    formBtns.forEach(function (formBtn) {
        formBtn.addEventListener("click", () => {
            window.removeEventListener("beforeunload", onBeforeunloadHandler);
        });
    });
});