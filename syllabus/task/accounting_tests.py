"""Unit Tests for Accountant"""

from print import print
import unittest
from accounting import Accountant, UpdatePacket


class Tests(unittest.TestCase):

    def test_accounting(self):

        accountant = Accountant(root='test-root')
        q = accountant.queue

        q.put(UpdatePacket(
            id='test-root',
            data={'start_time': 100, 'progress': 0.521},
            events=[
                {'body': 'test event', 'type': 'info', 'time': 100.10},
                {'body': 'test event 2', 'type': 'error', 'time': 101.50}],
            children=['test-child-1', 'test-child-2']))

        q.put(UpdatePacket(
            id='test-child-1',
            data={
                'start_time': 100.53,
                'end_time': 101.23,
                'foo': ['bar', 'baz']},
            events=[
                {'body': 'child event 1', 'type': 'warning', 'time': 100.60},
                {'body': 'child event 2', 'type': 'warning', 'time': 101.01}],
            children=[]))

        q.put(UpdatePacket(
            id='test-child-2',
            data={'foo': ['???']},
            events=[],
            children=[]))

        self.assertEqual(accountant.tree(), {
            "id": "test-root",
            "start_time": 100,
            "progress": 0.521,
            "events": [
                {'body': 'test event', 'type': 'info', 'time': 100.10},
                {'body': 'test event 2', 'type': 'error', 'time': 101.50}
            ],
            "children": [
                {
                    "id": "test-child-1",
                    'start_time': 100.53,
                    'end_time': 101.23,
                    "foo": ["bar", "baz"],
                    "events": [
                        {
                            'body': 'child event 1',
                            'type': 'warning',
                            'time': 100.60},
                        {
                            'body': 'child event 2',
                            'type': 'warning',
                            'time': 101.01}
                    ],
                    "children": []
                },
                {
                    "id": "test-child-2",
                    "foo": ["???"],
                    "events": [],
                    "children": []
                }
            ]
        })

        self.assertEqual(accountant.ordered_tree(), [
            (0, {
                'id': 'test-root',
                'progress': 0.521,
                'size': None,
                'name': None,
                'desc': None,
                'start_time': 100,
                'end_time': None}),
            (1, {'body': 'test event', 'type': 'info'}),
            (1, {
                'id': 'test-child-1',
                'progress': None,
                'size': None,
                'name': None,
                'desc': None,
                'start_time': 100.53,
                'end_time': 101.23}),
            (2, {'body': 'child event 1', 'type': 'warning'}),
            (2, {'body': 'child event 2', 'type': 'warning'}),
            (1, {'body': 'test event 2', 'type': 'error'}),
            (1, {
                'id': 'test-child-2',
                'progress': None,
                'size': None,
                'name': None,
                'desc': None,
                'start_time': None,
                'end_time': None})
        ])

        print(
            "\n\n"
            "Accountant Output -- Verify Manually\n"
            "------------------------------------\n\n")
        print(str(accountant))
        print("\n\n")

        accountant.stop()
        self.assertTrue(accountant.stopped)

    def test_circular_and_undefined(self):

        accountant = Accountant(root='root')
        q = accountant.queue

        q.put(UpdatePacket(
            id='root',
            data={'is_root': True},
            events=[],
            children=['undefined-child', 'root']))

        self.assertEqual(accountant.tree(), {
            "id": "root",
            "is_root": True,
            "events": [],
            "children": [
                {"id": "undefined-child"},
                {"id": "root"},
            ]
        })

        accountant.stop()
        self.assertTrue(accountant.stopped)
