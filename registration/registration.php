<?php
		session_start();
		function printResult ($set){
			$list = array();
			while (($row = $set->fetch_assoc()) != false){
				$list[] = $row["user_mail"];
			}
			return $list;
		}

		$tr = false;
        $t = true;
		if(isset($_POST["button"])){
			$mysqli = new mysqli ("localhost", "root", "", "incubatya");
			$mysqli->query ("SET NAMES 'utf8'");
			$mail = htmlspecialchars ($_POST["mail"]);
			$name = htmlspecialchars ($_POST["name"]);
			$pass1 = htmlspecialchars ($_POST["pass1"]);
			$pass2 = htmlspecialchars ($_POST["pass2"]);
			$code_word = htmlspecialchars ($_POST["code_word"]);
			
			$_SESSION["mail"] = $mail;
			$_SESSION["name"] = $name;
			$_SESSION["code_word"] = $code_word;
			$_SESSION["pass1"] = $pass1;
			$_SESSION["pass2"] = $pass2;
			
			$error_mail = "";
			$error_name = "";
			$error_code_word = "";
			$error_pass1 = "";
			$error_pass2 = "";
			
			$user_mail = $mysqli->query ("SELECT user_mail FROM users");
			$user_mail = printResult ($user_mail);
						
			if (!preg_match ("/@/", $mail) || in_array($mail, $user_mail)){
				if (in_array($mail, $user_mail)){
					$error_mail = "Account with this email adress already exists";
				}
				else{
					$error_mail = "Enter a valid email adress";
				}
			}
			if ($code_word == ""){
				$error_code_word = "You forgot the code word";
			}
			if ($name == ""){
				$error_name = "You forgot your name";
			}
			if ($pass1 == ""){
                $error_pass1 = "Enter a password";
			}
			if ($pass2 == ""){
                $error_pass2 = "Enter a password";
			}
			if ($pass1 != $pass2){
				$error_pass2 = "Passwords dont match";
            }
            if ($t == true){
			    if ($error_pass1 == "" and $error_code_word == "" and $error_mail == "" and $error_name == "" and $error_pass2 == "") {
                    $code_word = iconv ('CP1251', 'UTF-8', $code_word);
                    $mysqli->query ("INSERT INTO users (user_mail, user_name, user_password, user_code_word) VALUES ('$mail', '$name', '$pass1', '$code_word')");
					$t = false;
					$tr = true;
                }
            }
			$mysqli->close ();
		}
		require "registration.html";
?>