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
    openDatabase()
        .then(db => {
            getAllDataFromIndexedDB(db)
                .then(data => {
                    const reviewTable = document.querySelector('#review-table tbody'); // 表の要素を取得
                    let displayCount = Math.min(data.length, 20); // 20件以上なら20件まで表示

                    // データが存在するかチェック
                    if (displayCount > 0) {
                        // 既存の表にデータを追加
                        data.slice(0, displayCount).forEach((review, index) => {
                            const row = reviewTable.insertRow(); // 新しい行を作成
                            

                            let cellNo = row.insertCell(0);
                            let cellDate = row.insertCell(1);
                            let cellSentiment = row.insertCell(2);
                            let cellSummary = row.insertCell(3);
                            let cellOriginal = row.insertCell(4);

                            cellNo.textContent = index + 1;
                            cellDate.textContent = review.date; // 直接dateフィールドを使用
                            cellSentiment.textContent = review.sentiment;
                            cellSummary.textContent = review.summary;
                            cellOriginal.textContent = review.original; // 直接originalフィールドを使用
                        });
                    } else {
                        // データが無い場合はメッセージ表示
                        const errorMessageDiv = document.getElementById('errorMessage');
                        errorMessageDiv.textContent = '表示するレビューがありません。';
                    }
                })
                .catch(error => console.error("データ取得エラー: ", error));
        })
        .catch(error => console.error("Database error:", error));
}
