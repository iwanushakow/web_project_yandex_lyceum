<?php
    $t = false;
    session_start();
	function printResult ($set){
		$list = array();
		do{
			$list[] = $row["user_mail"];
		} while (($row = $set->fetch_assoc()) != false);
		return $list;
	}
	function Passwords ($set, $user_mail){
		$pass = "";
		do{
			if ($row["user_mail"] == $user_mail){
				$pass = $row["user_password"];
			}
		} while (($row = $set->fetch_assoc()) != false);
		return $pass;
	}
    if(isset($_POST["button"])){
		$mysqli = new mysqli ("localhost", "root", "", "incubatya");
	    $mysqli->query ("SET NAMES 'utf8'");
		
		$mail = htmlspecialchars ($_POST["mail"]);
		$password = htmlspecialchars ($_POST["password"]);
		
		$user_mail = $mysqli->query ("SELECT user_mail FROM users");
		$user_mail = printResult ($user_mail);
        
        $_SESSION["mail"] = $mail;
        $error_mail = "";
		$error_password = "";
        if (!in_array($mail, $user_mail)){
			$error_mail = "Аккаунта с такой почтой не существует";
		}
        else{
			$real_password = $mysqli->query ("SELECT * FROM users");
			$real_password = Passwords($real_password, $mail);
			
			if ($real_password != $password){
				$error_password = "incorrect password";
			}
			else{
				$t = true;
			}
        }			
	    $mysqli->close ();
	}
	require "sign_in.html";
?>