"""Example of Converting TextSum model data.
Usage:
python data_convert_example.py --command binary_to_text --in_file data/data --out_file data/text_data
python data_convert_example.py --command text_to_binary --in_file data/text_data --out_file data/binary_data
python data_convert_example.py --command binary_to_text --in_file data/binary_data --out_file data/text_data2
diff data/text_data2 data/text_data
"""

import struct
import sys

import tensorflow as tf
from tensorflow.core.example import example_pb2

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('command', 'binary_to_text',
                           'Either binary_to_text or text_to_binary.'
                           'Specify FLAGS.in_file accordingly.')
tf.app.flags.DEFINE_string('in_file', '', 'path to file')
tf.app.flags.DEFINE_string('out_file', '', 'path to file')

def _binary_to_text():
    reader = open(FLAGS.in_file, 'rb')
    writer = open(FLAGS.out_file, 'w')
    while True:
        len_bytes = reader.read(8)
        if not len_bytes:
            sys.stderr.write('Done reading\n')
            return
        str_len = struct.unpack('q', len_bytes)[0]
        tf_example_str = struct.unpack('%ds' % str_len, reader.read(str_len))[0]
        tf_example = example_pb2.Example.FromString(tf_example_str)
        examples = []
        for key in tf_example.features.feature:
            examples.append('%s=%s' % (key, tf_example.features.feature[key].bytes_list.value[0]))
        writer.write('%s\n' % '\t'.join(examples))
    reader.close()
    writer.close()

def text_to_binary(in_file_path, out_file_path):
    inputs = open(in_file_path, 'r').readlines()
    writer = open(out_file_path, 'wb')
    for inp in inputs:
        tf_example = example_pb2.Example()
        for feature in inp.strip().split('\t'):
            (k, v) = feature.split('=')
            tf_example.features.feature[k.encode('utf8')].bytes_list.value.extend([v.encode('utf8')])
        tf_example_str = tf_example.SerializeToString()
        str_len = len(tf_example_str)
        writer.write(struct.pack('q', str_len))
        writer.write(struct.pack('%ds' % str_len, tf_example_str))
    writer.close()

def main():
    text_to_binary('../yahoo_knowledge_data/data_ready', '../yahoo_knowledge_data/data')


if __name__ == '__main__':
    main()
