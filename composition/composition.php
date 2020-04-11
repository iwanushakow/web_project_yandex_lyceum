<?php
    $t = false;
    session_start();

    function block_id ($set){
        $id = 0;
        if (count($set) != 0){
            while (($row = $set->fetch_assoc()) != false){
                $id = $row["block_id"];
            }
        }
        return $id;
    }

    function previous_hash ($set){
        $name = "";
        while (($row = $set->fetch_assoc()) != false){
            $name = $row["this_hash"];
          }
        return $name;
      }
    
    function new_block($work_id, $user_id, $work_type, $work_date, $work_link, $comp_name){
        $mysqli = new mysqli ("localhost", "root", "", "incubatya");
        $mysqli->query ("SET NAMES 'utf8'");
        $list = $mysqli->query("SELECT this_hash FROM blockchain");
        $prervious_hash = previous_hash($list);
        $this_hash =  hash ("sha256", "'$work_id' '$user_id', '$work_type', '$work_date', '$work_link', '$prervious_hash', nezabudparol");
        $list = $mysqli->query("SELECT block_id FROM blockchain");
        $id = block_id($list) + 1;ч
        $mysqli->query("INSERT INTO blockchain(block_id, work_id, user_id, work_type, work_date, work_link, work_name, this_hash, previous_hash) VALUES('$id', '$work_id', '$user_id', '$work_type', '$work_date', '$work_link', '$comp_name', '$this_hash', '$prervious_hash')");
    }

    function work_id ($set){
        $id = 0;    
        if (count($set) != 0){
            while (($row = $set->fetch_assoc()) != false){
                $id = $row["work_id"];
            }
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
    $_SESSION["comp_name"] = $_POST["comp_name"];
    $comp_name = $_POST["comp_name"];
    $mail = $_GET["mail"];
    $mysqli = new mysqli ("localhost", "root", "", "incubatya");
    $mysqli->query ("SET NAMES 'utf8'");
    $list = $mysqli->query ("SELECT * FROM users");
    $id = id($list, $mail);

    if (isset($_FILES["file"])){
        $errors = array();
        $file_name = $_FILES["file"]["name"];
        $file_size = $_FILES["file"]["size"];
        $file_tmp = $_FILES["file"]["tmp_name"];
        $file_tmp = (string) $file_tmp;
        $file_type = $_FILES["file"]["type"];
        $file_type = explode("/", $file_type);
        $file_type = $file_type[0];
        $file_ext = strtolower(end(explode('.', $_FILES["file"]["name"])));
        
        if ($file_size > 2097152){
            $errors[] = "File should be 2mb";
        }
        if (empty($errors) == true and $file_tmp != ""){
            move_uploaded_file($file_tmp, "files/");
            $list = $mysqli->query ("SELECT work_id FROM works");
            $work_id = work_id($list) + 1;
            $date = date ("d-m-Y H:i");
            $mysqli->query("INSERT INTO works(work_id, user_id, work_type, work_date, work_link, work_name) VALUES('$work_id', '$id', '$file_type', '$date', '$file_tmp', '$comp_name')");
            new_block($work_id, $id, $file_type, $date, $file_tmp, $comp_name);
            $t = true;
        }
        else{
            print $errors;
        }
    }
    require "composition.html";
?>