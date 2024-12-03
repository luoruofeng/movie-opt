import argparse
from movie_opt.commands.create import create_pc, create_phone
from movie_opt.commands.subtitle import srt2ass

def main():
    parser = argparse.ArgumentParser(
        description="一个命令行工具将电影改为英语教程"
    )
    subparsers = parser.add_subparsers(dest="command", help="命令列表")

    # Command create 
    parser_create = subparsers.add_parser("create", help="通过字幕文件和视频创建新视频")
    subparser_create = parser_create.add_subparsers(dest="subcommand", help="create命令的子命令")
    
    # Command create -> Subcommand pc
    subparser_create_pc = subparser_create.add_parser("pc", help="创建pc视频")
    subparser_create_pc.add_argument("--path", required=False, help="包括了字幕和视频的路径")
    subparser_create_pc.set_defaults(func=create_pc)

    # Command create -> Subcommand phone
    subparser_create_phone = subparser_create.add_parser("phone", help="创建phone视频")
    subparser_create_phone.add_argument("--path", required=False, help="包括了字幕和视频的路径")
    subparser_create_phone.set_defaults(func=create_phone)

    #Command convert
    parser_convert = subparsers.add_parser("convert", help="格式转换")
    subparser_convert = parser_convert.add_subparsers(dest="subcommand", help="convert命令的子命令")
    
    # Command create -> Subcommand pc
    subparser_convert_srt2ass = subparser_convert.add_parser("srt2ass", help="srt -> ass 视频")
    subparser_convert_srt2ass.add_argument("--path", required=False, help="srt转化为ass")
    subparser_convert_srt2ass.set_defaults(func=srt2ass)


    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
