setInterval(updateTimes, 60000);
updateTimes();
hljs.configure({languages: []}); // Disable language-detection.
hljs.initHighlighting();

document.getElementById('nav-toggle-btn').addEventListener('click', function (e) {
    e.preventDefault();
    document.getElementById('nav-menu-list').classList.toggle('show');
});

function updateTimes() {
    var times = document.querySelectorAll('time.timeago');
    for (var i = times.length; i-- > 0;) {
        var d = Date.parse(times[i].getAttribute('datetime'));
        times[i].textContent = timeSince(d) + ' ago';
    }
}

function timeSince(date) {
    var seconds = Math.floor((new Date() - date) / 1000);
    var interval = Math.floor(seconds / 31536000);
    if (interval > 1) {
        return interval + " years";
    }
    interval = Math.floor(seconds / 2592000);
    if (interval > 1) {
        return interval + " months";
    }
    interval = Math.floor(seconds / 86400);
    if (interval > 1) {
        return interval + " days";
    }
    interval = Math.floor(seconds / 3600);
    if (interval > 1) {
        return interval + " hours";
    }
    interval = Math.floor(seconds / 60);
    if (interval > 1) {
        return interval + " minutes";
    }
    return Math.floor(seconds) + " seconds";
}
