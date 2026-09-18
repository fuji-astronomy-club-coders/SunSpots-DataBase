$w.onReady(function () {

    // HTMLコンポーネントからのメッセージを待機
    $w("#html1").onMessage((event) => {
        // HTML側から "ready" が届いたらJSONを渡す
        if (event.data === "ready") {
            sendCalendarData();
        }
    });

});

function sendCalendarData() {
    // Velo側で生成またはデータベースから取得するJSONデータ
    const calendarJson = {
        daysInMonth: 30, // 9月の総日数
        emptyBefore: 1,  // 月曜始まりの場合、9/1(火)の前に空セルが1つ必要
        items: {
            "1": {
                url: "https://www.youtube.com/watch?v=qe29NgNqJZw&list=RDqe29NgNqJZw&start_radio=1",
                img: "https://img.youtube.com/vi/qe29NgNqJZw/maxresdefault.jpg"
            },
            "2": {
                url: "https://youtu.be/限定公開URL_02",
                img: "https://img.youtube.com/vi/限定公開URL_02/maxresdefault.jpg"
            },
            "3": {
                url: "https://youtu.be/限定公開URL_03",
                img: "https://img.youtube.com/vi/限定公開URL_03/maxresdefault.jpg"
            }
            // データのない日は指定不要（自動的に日付のみが表示されます）
        }
    };

    // HTMLコンポーネント（#html1）にJSONを送信
    $w("#html1").postMessage(calendarJson);
}