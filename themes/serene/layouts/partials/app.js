setInterval(updateTimes, 60000);
updateTimes();

document.getElementById('nav-toggle-btn').addEventListener('click', function (e) {
    e.preventDefault();
    document.getElementById('nav-menu-list').classList.toggle('show');
});

document.querySelectorAll('a[rel="footnote"]').forEach(function (el) {
    var target = document.getElementById(el.getAttribute('href').slice(1));
    el.setAttribute('title', target.firstChild.textContent.trim());
});

function updateTimes() {
    var times = document.getElementsByTagName('time');
    for (var i = times.length; i-- > 0;) {
        times[i].title = times[i].textContent;
        times[i].textContent = timeSince(Date.parse(times[i].getAttribute('datetime')));
    }
}

function timeSince(date) {
    {{- $secondsPerDay := mul 24 3600 }}
    var seconds = Math.floor((new Date() - date) / 1000),
        interval = Math.floor(seconds / {{ mul 365 $secondsPerDay }});
    if (interval > 1)
        return interval + ' years ago';
    interval = Math.floor(seconds / {{ mul 30 $secondsPerDay }});
    if (interval > 1)
        return interval + ' months ago';
    interval = Math.floor(seconds / {{ $secondsPerDay }});
    if (interval > 1)
        return interval + ' days ago';
    return 'Today';
}
