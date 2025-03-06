import data_load_tool

if __name__ == "__main__":
    p = data_load_tool.attach("dlt_github_pipeline")
    info = p.normalize()
    print(info)
