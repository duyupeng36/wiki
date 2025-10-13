#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os

def main():
    os.system("gitbook install")
    os.system("gitbook build")
    os.system("cd _book && python -m http.server 4000")


if __name__ == "__main__":
    main()
