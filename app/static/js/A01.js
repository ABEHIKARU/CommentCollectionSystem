document.addEventListener("DOMContentLoaded", function () {
    // 開始日と終了日を入力するための要素を取得
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    // 今日の日付をISO形式で取得し、'T'で分割して最初の部分を使用
    const today = new Date().toISOString().split('T')[0];
    const minStartDate = '2012-03-06';  // 開始日を2012年3月6日に設定

    // 開始日と終了日の入力要素に最小値と最大値を設定
    startDateInput.setAttribute('min', minStartDate); // 開始日の最小値を設定
    startDateInput.setAttribute('max', today);         // 開始日の最大値を設定
    endDateInput.setAttribute('max', today);            // 終了日の最大値を設定

    // 開始日が変更されたときに終了日の最小値を更新
    startDateInput.addEventListener('change', function () {
        endDateInput.setAttribute('min', this.value); // 開始日の値を基に終了日の最小値を設定
    });

    // 初期状態で終了日の最小値を開始日と同じに設定
    endDateInput.setAttribute('min', startDateInput.value);

    // IndexedDBを全てクリアする関数
    function clearIndexedDB() {
        // データベースを削除するためのリクエストを作成
        const request = indexedDB.deleteDatabase("TranslationAnalysisDB");

        // 成功時の処理
        request.onsuccess = function () {
            console.log("IndexedDBが正常に削除されました");
        };

        // エラー時の処理
        request.onerror = function (event) {
            console.error("IndexedDBの削除に失敗しました:", event.target.errorCode);
        };

        // ブロックされている場合の警告
        request.onblocked = function () {
            console.warn("IndexedDBの削除がブロックされました。");
        };
    }

    // ページが読み込まれたときにIndexedDBをクリア
    clearIndexedDB();
});
