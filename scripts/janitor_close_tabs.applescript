-- janitor_close_tabs.applescript
-- 只關「明確 agent 殘留」的分頁: Google 搜尋結果頁、gviz 資料端點。
-- 白名單網域一律不關(登入/OAuth/Gmail/Keep/ChatGPT/dashboard/YouTube/廣告後台…)。
-- Drive 具名資料夾與 docs 因難以自動辨識 Owner 內容, 不自動關(交由 agent「誰開誰關」)。
-- 回傳關閉數量; Chrome 沒開或無權限時安全回 0 / 非零 exit。

on isKeep(u)
	set keeps to {"accounts.google.com", "wp-login", "wp-admin", "mail.google.com", "keep.google.com", "chatgpt.com", "127.0.0.1", "localhost", "youtube.com", "business.facebook", "business.google.com", "drive.google.com", "docs.google.com"}
	repeat with k in keeps
		if u contains k then return true
	end repeat
	return false
end isKeep

on isResidue(u)
	set res to {"google.com/search?", "/gviz/tq", "google.com/search%3F"}
	repeat with r in res
		if u contains r then return true
	end repeat
	return false
end isResidue

on run
	set closedCount to 0
	tell application "Google Chrome"
		if not (running) then return 0
		repeat with w in (every window)
			set toClose to {}
			repeat with t in (every tab of w)
				set u to (URL of t)
				if (my isResidue(u)) and not (my isKeep(u)) then set end of toClose to (id of t)
			end repeat
			repeat with tid in toClose
				try
					close (first tab of w whose id is tid)
					set closedCount to closedCount + 1
				end try
			end repeat
		end repeat
	end tell
	return closedCount
end run
