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
            reject(`Transaction error: ${event.target.errorCode}`);
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

// サンプルのレビューデータ
const reviews = [
    { at: "2024-08-23", sentiment: "positive", summary: "Highly recommended", content: "Great product!" },
    { at: "2024-08-24", sentiment: "negative", summary: "Not as expected", content: "Disappointed with the quality." }
];

// IndexedDBにレビューを保存し、その後すべてのデータを読み込んで表示
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
