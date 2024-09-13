document.addEventListener("DOMContentLoaded", function () {
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');

    const today = new Date().toISOString().split('T')[0];
    const minStartDate = '2012-03-06';  // 開始日を2012年3月6日に設定

    startDateInput.setAttribute('min', minStartDate);
    startDateInput.setAttribute('max', today);
    endDateInput.setAttribute('max', today);

    startDateInput.addEventListener('change', function () {
        endDateInput.setAttribute('min', this.value);
    });

    endDateInput.setAttribute('min', startDateInput.value);

    // IndexedDBを全てクリアする関数
    function clearIndexedDB() {
        const request = indexedDB.deleteDatabase("TranslationAnalysisDB");

        request.onsuccess = function () {
            console.log("IndexedDBが正常に削除されました");
        };

        request.onerror = function (event) {
            console.error("IndexedDBの削除に失敗しました:", event.target.errorCode);
        };

        request.onblocked = function () {
            console.warn("IndexedDBの削除がブロックされました。");
        };
    }

    // ページが読み込まれたときにIndexedDBをクリア
    clearIndexedDB();
});