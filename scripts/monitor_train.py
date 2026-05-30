import time, os, datetime, sys
p = os.path.join(os.getcwd(), 'train_run_longer.log')
while True:
    try:
        if os.path.exists(p):
            st = os.stat(p)
            print(f"{datetime.datetime.now()} size={st.st_size}")
            with open(p, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.read().splitlines()
            for L in lines[-20:]:
                print(L)
        else:
            print(f"{datetime.datetime.now()} log missing")
    except Exception as e:
        print(f"{datetime.datetime.now()} monitor error: {e}")
    sys.stdout.flush()
    time.sleep(120)
