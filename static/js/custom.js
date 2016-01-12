function range(start, count) {
    return Array.apply(0, new Array(count))
        .map(function (element, index) {
            return index + start;
        });
}
function getQueryParam(url, key) {
    var queryStartPos = url.indexOf('?');
    if (queryStartPos === -1) {
        return;
    }
    var params = url.substring(queryStartPos + 1).split('&');
    for (var i = 0; i < params.length; i++) {
        var pairs = params[i].split('=');
        if (decodeURIComponent(pairs.shift()) == key) {
            return decodeURIComponent(pairs.join('='));
        }
    }
}
// Course.Detail
function changePage(page) {
    var startPage;
    if (page < 5) {
        startPage = 1
    } else {
        startPage = page - 4
    }
    if (page != 1) {
        $(".lastPage").attr('class', 'waves-effect lastPage')
    } else {
        $(".lastPage").attr('class', 'disabled lastPage')
    }
    $(".commentPage").each(function () {
        $(this).children("a").text(startPage++);
        if ($(this).text() == page) {
            $(this).attr('class', 'active commentPage')
        } else {
            $(this).attr('class', 'waves-effect commentPage')
        }
    });
    $("#comment").load("/course/" + $("input[name=CourseId]").attr("value") + "/page/" + page)
}
$(document).ready(function () {
    $("#comment").load("/course/" + $("input[name=CourseId]").attr("value") + "/page/" + $(".active.commentPage").text())
    $('select').material_select();
    switch (parseInt(getQueryParam(window.location.href, "code"))) {
        case -1:
            Materialize.toast("您已经评价该这门课程，不能重复评价", 5000);
            break;
        case 0:
            Materialize.toast("操作失败，请检查您的参数或与管理员联系", 5000);
            break;
        case 1:
            Materialize.toast("操作成功", 5000);
            break;
        case 2:
            Materialize.toast("课程添加成功，并将在管理员审核后显示", 5000);
            break;
    }
    $('input[name="StudentId"]').val(Cookies.get("StudentId"));
    $('input[name="NickName"]').val(Cookies.get("NickName"))
});
$(".commentPage").click(function () {
    changePage($(this).text())
});
$(".lastPage").click(function () {
    changePage(parseInt($(".active.commentPage").text()) - 1)
});
$(".nextPage").click(function () {
    changePage(parseInt($(".active.commentPage").text()) + 1)
});
// Add comment
$("a#add_comment").click(function () {
    $("#write_comment_box").openModal();
});
// Filter
$("input#filter").keyup(function () {
    $.uiTableFilter($("table#course"), this.value)
});
// Cookie
$("form#newComment").submit(function () {
    Cookies.set("StudentId", $('input[name="StudentId"]').val(), {expires: 30, secure: true});
    Cookies.set("NickName", $('input[name="NickName"]').val(), {expires: 30, secure: true})
});