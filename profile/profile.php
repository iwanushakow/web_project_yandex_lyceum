<?php
    session_start();
    function get_all ($set){
      $heads = array();
      $texts = array();
      $times = array();
      $links = array();
      while (($row = $set->fetch_assoc()) != false) {
        $heads[] = $row["post_headline"];
        $texts[] = $row["post_text"];
        $times[] = $row["post_date"];
        $links[] = $row["work_link"];
      }
      return array($heads, $texts, $times, $links);
    }

    function printResult ($set){
      $id = "";
      $name = "";
      while (($row = $set->fetch_assoc()) != false){
        $name = $row["user_nick"];
        $id = $row["user_id"];
      }
      return array($name, $id);
    }
    $p = false;
    $c = false;
    $o = false;
    $mail = $_GET["mail"];
    $mysqli = new mysqli ("localhost", "root", "", "incubatya");
    $mysqli->query ("SET NAMES 'utf8'");
    $list = $mysqli->query ("SELECT * FROM users WHERE user_mail='$mail'");
    $list = printResult($list);
    $name = $list[0];
    $id = $list[1];
    $name = iconv ('UTF-8', 'CP1251', $name);

    $posts = $mysqli->query ("SELECT * FROM posts WHERE user_id='$id'");
    $list = get_all($posts);
    $heads = $list[0];
    $text = $list[1];
    $time = $list[2];
    $link = $list[3];
    if (isset($_POST["post"])){
      $p = true;
    }
    if (isset($_POST["composition"])){
      $c = true;
    }
    if (isset($_POST["work"])){
      $o = true;
    }
    if (!$p && !$c && !$o){
      for ($i = 0; $i < count($text); $i++){
        echo $heads[$i]."<br />";
        echo $time[$i]."<br />";
        echo "<textarea rows=10 cols=30 placeholder='$text[$i]' readonly></textarea><br />";
        echo "<label>$link[$i]</label><br /><br /><br />";
      }
    }
    require "profile.html";
?>