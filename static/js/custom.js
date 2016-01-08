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
    $("#course").load("/course/page/" + $(".active.coursePage").text())
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

// Course
function changePage1(page) {
    var startPage;
    if (page < 5) {
        startPage = 1
    } else {
        startPage = page - 4
    }
    if (page != 1) {
        $(".lastPage1").attr('class','waves-effect lastPage1')
    } else {
        $(".lastPage1").attr('class','disabled lastPage1')
    }
    $(".coursePage").each(function () {
        $(this).children("a").text(startPage++);
        if ($(this).text() == page) {
            $(this).attr('class','active coursePage')
        } else {
            $(this).attr('class','waves-effect coursePage')
        }
    });
    $("#course").load("/course/page/" + page)
}
$(".coursePage").click(function () {
    changePage1($(this).text())
});
$(".lastPage1").click(function () {
    changePage1(parseInt($(".active.coursePage").text()) - 1)
});
$(".nextPage1").click(function () {
    changePage1(parseInt($(".active.coursePage").text()) + 1)
});

// Add comment
$("a#add_comment").click(function () {
    $("#write_comment_box").openModal();
});
