# -*- coding: utf-8 -*-

import argparse
from fetcher.twstock.cli import best_four_point
from fetcher.twstock.cli import stock
from fetcher.twstock.cli import realtime


def run():
    parser = argparse.ArgumentParser()

    parser.add_argument('-b', '--bfp', nargs='+')
    parser.add_argument('-s', '--stock', nargs='+')
    parser.add_argument('-r', '--realtime', nargs='+')
    args = parser.parse_args()

    if args.bfp:
        best_four_point.run(args.bfp)
    elif args.stock:
        stock.run(args.stock)
    elif args.realtime:
        realtime.run(args.realtime)
