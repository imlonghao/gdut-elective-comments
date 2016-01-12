function range(start, count) {
    return Array.apply(0, new Array(count))
        .map(function (element, index) {
            return index + start;
        });
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
        $(".lastPage").attr('class','waves-effect lastPage')
    } else {
        $(".lastPage").attr('class','disabled lastPage')
    }
    $(".commentPage").each(function () {
        $(this).children("a").text(startPage++);
        if ($(this).text() == page) {
            $(this).attr('class','active commentPage')
        } else {
            $(this).attr('class','waves-effect commentPage')
        }
    });
    $("#comment").load("/course/" + $("input[name=CourseId]").attr("value") + "/page/" + page)
}
$(document).ready(function () {
    $("#comment").load("/course/" + $("input[name=CourseId]").attr("value") + "/page/" + $(".active.commentPage").text())
    $('select').material_select();
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
$("input#filter").keyup(function (){
    $.uiTableFilter($("table#course"), this.value)
});