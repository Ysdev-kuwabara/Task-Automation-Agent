from agent import run_agent

if __name__ == "__main__":
    #ファイル整理
    content=input("Enter your Proposal : ")
    #現在のディレクトリのファイル一覧を確認して、内容をまとめたREADME.mdを作成してください
    run_agent(content)