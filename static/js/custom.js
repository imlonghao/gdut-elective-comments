function range(start, count) {
    return Array.apply(0, new Array(count))
        .map(function (element, index) {
            return index + start;
        });
}
$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    return results[1] || 0;
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
    switch (parseInt($.urlParam("code"))) {
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