<?php
    $t = false;
    session_start();
    function linker($set){
        $id = "";
        while (($row = $set->fetch_assoc()) != false){
            $id = $row["work_link"];
            }
        return $id;
    }
    function id ($set, $mail){
        $id = "";
        while (($row = $set->fetch_assoc()) != false){
            if ($row["user_mail"] == $mail){
                $id = $row["user_id"];
            }
        }
        return $id;
    }
    function post_id ($set){
        $id = "";
        while (($row = $set->fetch_assoc()) != false){
            if ($row["user_mail"] == $mail){
                $id = $row["post_id"];
            }
        }
        return $id;
    }
    if (isset($_POST["post"])){
        $error = "";
        $work_link = $_POST["works"];

        $mysqli = new mysqli ("localhost", "root", "", "incubatya");
        $mysqli->query ("SET NAMES 'utf8'");
        $list = $mysqli->query ("SELECT * FROM users");
        $mail = htmlspecialchars ($_GET["mail"]);
        $id = id($list, $mail);
        if ($work_link != "none"){
            $work_link = $mysqli->query ("SELECT work_link FROM works WHERE work_name='$work_link' AND user_id='$id'");
            $work_link = linker($work_link);
            $w = true;
        }
        else{
            $w = false;
        }
        $head = htmlspecialchars ($_POST["post_head"]);
            $text = htmlspecialchars ($_POST["post_text"]);

            $_SESSION["post_head"] = $head;

            $list = $mysqli->query ("SELECT post_id FROM posts");
            $post_id = post_id($list) + 1;
            if ($head != "" && $text != ""){
                $date = date ("d-m-Y H:i");
                if ($w){
                    $mysqli->query ("INSERT INTO posts(post_id, user_id, post_date, post_text, post_headline, work_link) VALUES ('$post_id', '$id', '$date', '$text', '$head', '$work_link')");
                }
                else {
                    $mysqli->query ("INSERT INTO posts(post_id, user_id, post_date, post_text, post_headline) VALUES ('$post_id', '$id', '$date', '$text', '$head')");
                }
                $mysqli->close ();
                $t = true;
            }
            else {
                $t = false;
                $error = "can not publicate an empty post";
            }
        }
	require ("post.html");
?>