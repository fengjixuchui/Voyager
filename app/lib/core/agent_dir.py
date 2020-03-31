from app import mongo
from app.config import DOCKER_CLIENT
from app.lib.core import waf_check
from app.lib.handler.decorator import threaded
from app.lib.core import formatnum

import datetime
import threading
import time
import queue
import json

THREADS = 10


class ControllerDirs():
    # # 控制并发线程数
    # threads_queue = queue.Queue(maxsize=THREADS)
    # for i in range(THREADS):
    #     threads_queue.put_nowait(" ")

    # 存放目标线程数
    target_queue = queue.Queue()

    # list_queue = queue.Queue()

    def __init__(self, method, task_name, project, pid):

        self.task_name = task_name
        self.project = project
        self.pid = pid

        self.method = method

    # waf检查函数
    def _waf_check(self):

        list_queue = queue.Queue()

        if self.method == "adam":

            ports = mongo.db.ports.find({"parent_name": self.task_name})
            domains = mongo.db.subdomains.find({"parent_name": self.task_name})

            for i in domains:
                new_dict = dict()
                new_dict["http_address"] = i["http_address"]
                new_dict["keydict"] = "asp.txt,common.txt,jsp.txt,php.txt"
                new_dict["parent_name"] = self.project
                new_dict["pid"] = self.pid
                self.target_queue.put_nowait(new_dict)

            for j in ports:
                if any([j["service"] == "http", j["service"] == "http-proxy", j["service"] == "https"]) \
                        and j["http_address"] != "unknown" and "keydict" in j:
                    new_dict = dict()
                    new_dict["http_address"] = j["http_address"]
                    new_dict["keydict"] = j["keydict"]
                    new_dict["parent_name"] = self.project
                    new_dict["pid"] = self.pid

                    self.target_queue.put_nowait(new_dict)

            while True:

                sess = mongo.db.tasks.find_one({"id": self.pid})

                # 项目被删除的时候
                if sess is None:
                    return True

                target_list = list()

                if self.target_queue.qsize() == 0:
                    break

                if self.target_queue.qsize() >= THREADS:

                    # 使用攻击对象attactObject的线程数来控制是否要启动新的线程
                    for index in range(0, THREADS):
                        # self.threads_queue.get()
                        param = self.target_queue.get()
                        attacker = threading.Thread(target=waf_check, args=(param, list_queue))
                        attacker.start()
                        target_list.append(attacker)


                else:
                    for index in range(0, self.target_queue.qsize()):
                        # self.threads_queue.get()
                        param = self.target_queue.get()
                        attacker = threading.Thread(target=waf_check, args=(param, list_queue))
                        attacker.start()
                        target_list.append(attacker)

                # And wait for them to all finish
                alive = True
                while alive:
                    alive = False
                    for thread in target_list:
                        if thread.is_alive():
                            alive = True
                            time.sleep(0.1)

            return list(list_queue.queue)

        if self.method == "lilith":

            sess = mongo.db.tasks.find_one({"id": self.pid})

            # 项目被删除的时候
            if sess is None:
                return "flag"

            target_list = list()

            target_content = sess["target"]

            for k in json.loads(target_content):
                self.target_queue.put_nowait(k)

            while True:

                if self.target_queue.qsize() == 0:
                    break

                if self.target_queue.qsize() >= THREADS:

                    # 使用攻击对象attactObject的线程数来控制是否要启动新的线程
                    for index in range(0, THREADS):
                        # self.threads_queue.get()
                        param = self.target_queue.get()
                        attacker = threading.Thread(target=waf_check, args=(param, list_queue))
                        attacker.start()
                        target_list.append(attacker)


                else:
                    for index in range(0, self.target_queue.qsize()):
                        # self.threads_queue.get()
                        param = self.target_queue.get()
                        attacker = threading.Thread(target=waf_check, args=(param, list_queue))
                        attacker.start()
                        target_list.append(attacker)

                alive = True
                while alive:
                    alive = False
                    for thread in target_list:
                        if thread.is_alive():
                            alive = True
                            time.sleep(0.1)

            return list(list_queue.queue)

    def dir_scan(self, info):

        sess = mongo.db.tasks.find_one({"id": self.pid})

        # 项目被删除的时候
        if sess is None:
            return True

        if len(info) == 0:
            mongo.db.tasks.update_one(
                {"id": self.pid},
                {'$set': {
                    'progress': "100.00%",
                    'status': 'Finished',
                    'end_time': datetime.datetime.now(),
                    'live_host': 0,

                }
                }
            )

            return True

        mongo.db.tasks.update_one(
            {"id": self.pid},
            {'$set': {
                'target': json.dumps(info, ensure_ascii=False),
                'hidden_host': len(info),

            }
            }
        )

        for i in info:
            target = str(json.dumps(i, ensure_ascii=False))

            contain = DOCKER_CLIENT.containers.run("ap0llo/dirsearch:0.3.9", [target], detach=True,
                                                   network="host")

            mongo.db.tasks.update_one(
                {"id": self.pid},
                {'$set': {
                    'contain_id': contain.id

                }
                }
            )

            # 心跳线程用来更新任务状态
            while True:

                time.sleep(3)

                task_dir = mongo.db.tasks.find_one({"id": self.pid})
                if task_dir is None:
                    return

                process_json = json.loads(task_dir["total_host"])

                if len(process_json) == 0:
                    time.sleep(10)

                tasks_num = task_dir["hidden_host"]

                now_progress = 0
                # 统计总任务进度
                for k, v in process_json.items():
                    progress_ = formatnum(v)
                    now_progress = now_progress + progress_

                progress = '{0:.2f}%'.format(now_progress / tasks_num)

                if progress == "100.00%":
                    mongo.db.tasks.update_one(
                        {"id": self.pid},
                        {'$set': {
                            'progress': "100.00%",
                            'status': "Finished",
                            "end_time": datetime.datetime.now()
                        }
                        }
                    )
                    return

                if DOCKER_CLIENT.containers.get(contain.id).status == "running":
                    mongo.db.tasks.update_one(
                        {"id": self.pid},
                        {'$set': {
                            'progress': progress,

                        }
                        }
                    )

                else:

                    task_collection = mongo.db.tasks.find_one({"id": self.pid})

                    # 如果任务不存在了，直接结束任务。
                    if task_collection is None:
                        return True

                    json_target = json.loads(task_collection.get("total_host", "{}"))

                    json_target[i.get("http_address")] = "100.00%"

                    mongo.db.tasks.update_one(
                        {"id": self.pid},
                        {'$set': {
                            'total_host': json.dumps(json_target, ensure_ascii=False),

                        }
                        }
                    )

                    # 用来判断任务没有开始就结束的逻辑
                    new_task_dir = mongo.db.tasks.find_one({"id": self.pid})
                    if task_dir is None:
                        return

                    tasks_num = new_task_dir["hidden_host"]

                    json_process = json.loads(new_task_dir["total_host"])

                    now_progress = 0
                    # 统计总任务进度
                    for k, v in json_process.items():
                        progress_ = formatnum(v)
                        now_progress = now_progress + progress_

                    progress = '{0:.2f}%'.format(now_progress / tasks_num)

                    if progress == "100.00%":
                        mongo.db.tasks.update_one(
                            {"id": self.pid},
                            {'$set': {
                                'progress': "100.00%",
                                'status': "Finished",
                                "end_time": datetime.datetime.now()
                            }
                            }
                        )
                        return

                    break

    @classmethod
    @threaded
    def thread_start(cls, method, task_name, project, pid):

        while True:

            task = mongo.db.tasks.find_one({'id': pid})

            if task is None:
                return True

            if mongo.db.tasks.find({'status': "Running", "hack_type": "目录扫描"}).count() > 0:
                mongo.db.tasks.update_one(
                    {"id": pid},
                    {'$set': {
                        'status': 'Waiting',
                    }
                    }
                )
                time.sleep(5)

            else:

                mongo.db.tasks.update_one(
                    {"id": pid},
                    {'$set': {
                        'status': 'Running',
                    }
                    }
                )

                break

        app = cls(method=method, task_name=task_name, project=project, pid=pid)
        # 类http标签进行waf检查
        info = app._waf_check()

        if info == "flag":
            mongo.db.tasks.update_one(
                {"id": pid},
                {'$set': {
                    'progress': "100.00%",
                    'status': 'Finished',
                    'end_time': datetime.datetime.now(),
                    'live_host': 0,

                }
                }
            )

            return True

        app.dir_scan(info)
