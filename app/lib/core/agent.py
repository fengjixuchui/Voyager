from app.config import DOCKER_CLIENT
from app.lib.handler.decorator import threaded
from app.lib.core import formatnum
from app import mongo

import time
import datetime
import json


class Controller(object):
    """
    用来控制docker任务的核心函数
    """

    @staticmethod
    @threaded
    def stop_contain(contain_id):
        """
        用来终止启动的容器
        :param contain_id:8462ccf520899aff47b7bdb6b8f0fa65cc43f24c214a26dd94f2d58425bd6799
        :return:
        """

        try:

            if DOCKER_CLIENT.containers.get(contain_id).status == "running":
                docker_object = DOCKER_CLIENT.containers.get(contain_id)
                docker_object.stop()

                return True
            else:

                return True
        except:
            return False

    @staticmethod
    @threaded
    def subdomain_scan(uid):
        """
        添加域名扫描任务
        :param domain: example.com
        :param uid: c2385a01-bb0a-40a3-8694-05a31a440ba6
        :return:
        """

        # 有任务在执行的时候先暂停
        while True:

            time.sleep(3)

            task = mongo.db.tasks.find_one({'id': uid})

            if task is None:
                return True

            if mongo.db.tasks.find({'status': "Running", "hack_type": "域名扫描"}).count() > 0:
                mongo.db.tasks.update_one(
                    {"id": uid},
                    {'$set': {
                        'status': 'Waiting',
                    }
                    }
                )
                time.sleep(5)

            else:

                mongo.db.tasks.update_one(
                    {"id": uid},
                    {'$set': {
                        'status': 'Running',
                    }
                    }
                )

                break

        taskCollection = mongo.db.tasks.find_one({"id": uid})
        if taskCollection is None:
            return True

        targetList = taskCollection["target"].split(",")
        parentName = taskCollection["parent_name"]
        tasks_num = taskCollection["live_host"]

        for t in targetList:
            newTarget = dict()
            newTarget["Purpose"] = t
            newTarget["parentName"] = parentName
            newTarget["pid"] = uid

            infoString = str(json.dumps(newTarget, ensure_ascii=False))

            contain = DOCKER_CLIENT.containers.run("ap0llo/oneforall:0.1.0", [infoString], detach=True, remove=True,
                                                   auto_remove=True,
                                                   network="host")

            newTaskCollection = mongo.db.tasks.find_one({"id": uid})
            json_target = json.loads(newTaskCollection.get("hidden_host"))

            json_target[t] = "0.00%"

            mongo.db.tasks.update_one({"id": uid}, {
                "$set": {"contain_id": contain.id, 'hidden_host': json.dumps(json_target, ensure_ascii=False)}})

            # 心跳线程用来更新任务状态
            while True:

                time.sleep(3)

                task_dir = mongo.db.tasks.find_one({"id": uid})
                if task_dir is None:
                    return True

                process_json = json.loads(task_dir.get("hidden_host"))

                if len(process_json) == 0:
                    time.sleep(10)

                now_progress = 0
                # 统计总任务进度
                for k, v in process_json.items():
                    progress_ = formatnum(v)
                    now_progress = now_progress + progress_

                progress = '{0:.2f}%'.format(now_progress / tasks_num)

                if progress == "100.00%":
                    mongo.db.tasks.update_one(
                        {"id": uid},
                        {'$set': {
                            'progress': "100.00%",
                            'status': "Finished",
                            "end_time": datetime.datetime.now()
                        }
                        }
                    )
                    return

                else:
                    mongo.db.tasks.update_one(
                        {"id": uid},
                        {'$set': {
                            'progress': progress,
                        }
                        }
                    )

                task_collection = mongo.db.tasks.find_one({"id": uid})

                # 如果任务不存在了，直接结束任务。
                if task_collection is None:
                    return True

                json_target = json.loads(task_collection.get("hidden_host"))

                if json_target[t] == "100.00%":
                    break

        mongo.db.tasks.update_one(
            {"id": uid},
            {'$set': {
                'progress': "100.00%",
                'status': "Finished",
                "end_time": datetime.datetime.now(),
                "contain_id": "Null",
            }
            }
        )

    @staticmethod
    @threaded
    def ports_scan(uid):
        """
        添加域名扫描任务
        :param domain: example.com
        :param uid: c2385a01-bb0a-40a3-8694-05a31a440ba6
        :return:
        """

        # 有任务在执行的时候先暂停
        while True:

            task = mongo.db.tasks.find_one({'id': uid})

            if task is None:
                return True

            if mongo.db.tasks.find({'status': "Running", "hack_type": "端口扫描"}).count() > 0:
                mongo.db.tasks.update_one(
                    {"id": uid},
                    {'$set': {
                        'status': 'Waiting',
                    }
                    }
                )
                time.sleep(5)

            else:

                mongo.db.tasks.update_one(
                    {"id": uid},
                    {'$set': {
                        'status': 'Running',
                    }
                    }
                )

                break

        contain = DOCKER_CLIENT.containers.run("ap0llo/nmap:7.80", [uid], remove=True, detach=True,
                                               auto_remove=True,
                                               network="host")

        mongo.db.tasks.update_one({"id": uid}, {"$set": {"contain_id": contain.id}})

        return True
