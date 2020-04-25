<?php
    function hashes($set){
        $list = array();
        while (($row = $set->fetch_assoc()) != false){
            $lst = array();
            $lst[] = $row["this_hash"];
            $lst[] = $row["previous_hash"];
            $list[] = $lst;
        }
        return $list;
    }


    function values($set){
        $list = array();
        while (($row = $set->fetch_assoc()) != false){
            $lst = array();
            $lst[] = $row["work_id"];
            $lst[] = $row["user_id"]; 
            $lst[] = $row["work_type"];
            $lst[] = $row["work_date"];
            $lst[] = $row["work_link"];
            $list[] = $lst;
        }
        return $list;
    }
    $mysqli = new mysqli ("localhost", "root", "", "incubatya");
    $mysqli->query ("SET NAMES 'utf8'");

    $list = $mysqli->query("SELECT * FROM blockchain");
    $block_chain = values($list);

    $list = $mysqli->query("SELECT * FROM blockchain");
    $hashes = hashes($list);

    $works = $mysqli->query("SELECT * FROM works");
    $works = values($works);
    $o = 0;
    echo "Checking hashes: <br />";
    for ($i = 0; $i < count($hashes) - 1; $i++){
        if ($hashes[$i][0] != $hashes[$i + 1][1]){
            $o = $i + 1;
            echo "problem in block $o<br />";
        }
        else{
            $o = $i + 1;
            echo "everything alright in block $o<br />";
        }
    }
    $o++;
    echo "everything alright in block $o<br />";
    echo "<br />";
    echo "Comparing tables: <br />";
    for ($i = 0; $i < count($works); $i++){
        $t = true;
        for ($j = 0; $j < count($works[$i]); $j++){
            if ($block_chain[$i][$j] != $works[$i][$j]){
                $t = false;
            }
        }
        if (!$t){
            $o = $i + 1;
            echo "problem in block $o<br />";
        }
        else {
            $o = $i + 1;
            echo "values match in block $o<br />";
        }
    }
?>