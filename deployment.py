#!/usr/bin/env python3
"""
Docker Compose 自动部署脚本
支持功能: init, start, restart, stop, delete
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

class DockerComposeDeployer:
    def __init__(self, compose_file="docker-compose.yml", project_dir="."):
        self.compose_file = compose_file
        self.project_dir = project_dir
        self.full_compose_path = os.path.join(project_dir, compose_file)
        
        # 检查 docker-compose 是否可用
        if not self._check_docker_compose():
            print("错误: 未找到 docker-compose 命令，请确保 Docker 和 Docker Compose 已安装")
            sys.exit(1)
    
    def _check_docker_compose(self):
        """检查 docker-compose 是否可用"""
        try:
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"检测到: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # 尝试使用 docker compose plugin
            try:
                result = subprocess.run(
                    ["docker", "compose", "version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"检测到: Docker Compose plugin")
                self.use_plugin = True
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False
    
    def _run_compose_command(self, command, args=None):
        """执行 docker-compose 命令"""
        if args is None:
            args = []
        
        # 构建完整的命令
        if hasattr(self, 'use_plugin') and self.use_plugin:
            base_cmd = ["docker", "compose"]
        else:
            base_cmd = ["docker-compose"]
        
        # 添加项目目录和配置文件
        if self.project_dir != ".":
            base_cmd.extend(["--project-directory", self.project_dir])
        
        if self.compose_file != "docker-compose.yml":
            base_cmd.extend(["-f", self.full_compose_path])
        
        full_cmd = base_cmd + command + args
        
        print(f"执行命令: {' '.join(full_cmd)}")
        
        try:
            result = subprocess.run(
                full_cmd,
                check=True,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            return False
    
    def init(self):
        """初始化 - 构建镜像"""
        print("================================ 初始化部署 ================================")
        if not os.path.exists(self.full_compose_path):
            print(f"错误: 未找到 docker-compose 文件: {self.full_compose_path}")
            return False
        
        print("构建 Docker 镜像...")
        return self._run_compose_command(["build"])
    
    def start(self):
        """启动服务"""
        print("================================ 启动服务 ================================")
        if not os.path.exists(self.full_compose_path):
            print(f"错误: 未找到 docker-compose 文件: {self.full_compose_path}")
            return False
        
        print("启动所有服务...")
        return self._run_compose_command(["up", "-d"])
    
    def restart(self):
        """重启服务
        删除 -> 初始化 -> 启动
        """
        print("================================ 重启服务 ================================")
        if not os.path.exists(self.full_compose_path):
            print(f"错误: 未找到 docker-compose 文件: {self.full_compose_path}")
            return False
        
        print("重启所有服务...")
        flag = self.delete()
        flag &= self.init()
        flag &= self.start()
        return flag
    
    def stop(self):
        """停止服务"""
        print("================================ 停止服务 ================================")
        if not os.path.exists(self.full_compose_path):
            print(f"错误: 未找到 docker-compose 文件: {self.full_compose_path}")
            return False
        
        print("停止所有服务...")
        return self._run_compose_command(["stop"])
    
    def delete(self):
        """删除服务（停止并移除容器、网络等）"""
        print("================================ 删除服务 ================================")
        if not os.path.exists(self.full_compose_path):
            print(f"错误: 未找到 docker-compose 文件: {self.full_compose_path}")
            return False
        
        print("停止并移除所有服务...")
        return self._run_compose_command(["down", "--rmi", "all"])
    
    def status(self):
        """查看服务状态"""
        print("================================ 服务状态 ================================")
        if not os.path.exists(self.full_compose_path):
            print(f"错误: 未找到 docker-compose 文件: {self.full_compose_path}")
            return False
        
        print("查看服务状态...")
        return self._run_compose_command(["ps"])
    
    def logs(self, service=None, follow=False, tail=100):
        """查看日志"""
        print("================================ 服务日志 ================================")
        args = []
        if follow:
            args.append("-f")
        args.extend(["--tail", str(tail)])
        if service:
            args.append(service)
        
        return self._run_compose_command(["logs"], args)

def main():
    parser = argparse.ArgumentParser(description="Docker Compose 自动部署脚本")
    parser.add_argument(
        "action",
        default="start",
        choices=["init", "start", "restart", "stop", "delete", "status", "logs"],
        help="要执行的操作"
    )
    parser.add_argument(
        "-f", "--file",
        default="docker-compose.yml",
        help="Docker Compose 文件路径 (默认: docker-compose.yml)"
    )
    parser.add_argument(
        "-d", "--directory",
        default=".",
        help="项目目录路径 (默认: 当前目录)"
    )
    parser.add_argument(
        "--service",
        help="指定服务（用于 logs 命令）"
    )
    parser.add_argument(
        "--follow",
        action="store_true",
        help="跟随日志输出（用于 logs 命令）"
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=100,
        help="显示最后多少行日志（用于 logs 命令）"
    )
    
    args = parser.parse_args()
    
    # 创建部署器实例
    deployer = DockerComposeDeployer(args.file, args.directory)
    
    # 执行对应操作
    if args.action == "init":
        success = deployer.init()
    elif args.action == "start":
        success = deployer.start()
    elif args.action == "restart":
        success = deployer.restart()
    elif args.action == "stop":
        success = deployer.stop()
    elif args.action == "delete":
        success = deployer.delete()
    elif args.action == "status":
        success = deployer.status()
    elif args.action == "logs":
        success = deployer.logs(args.service, args.follow, args.tail)
    else:
        print(f"未知操作: {args.action}")
        sys.exit(1)
    
    if success:
        print(f"操作 '{args.action}' 执行成功")
        sys.exit(0)
    else:
        print(f"操作 '{args.action}' 执行失败")
        sys.exit(1)

if __name__ == "__main__":
    main()