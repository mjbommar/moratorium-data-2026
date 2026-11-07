import json
import multiprocessing
import os
from pathlib import Path
import tempfile
import unittest

from bc_core.budget import BudgetExceeded
from scripts.private_run_storage import PrivateRunStorage, StorageBudgetExceeded


def worker(root, limit, gate, results):
    store = PrivateRunStorage(root, limit)
    gate.wait()
    try:
        store.append_jsonl('records', 'x' * 100)
        results.put(True)
    except StorageBudgetExceeded:
        results.put(False)


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def store_with_room(self, room):
        # Policy length depends on the decimal representation of the cap.
        limit = room + 1000
        for _ in range(10):
            policy = {'root': str(self.root.resolve()), 'max_bytes': limit}
            new = room + len((json.dumps(policy, sort_keys=True, ensure_ascii=False) + '\n').encode())
            if new == limit:
                break
            limit = new
        return PrivateRunStorage(self.root, limit)

    def test_exact_append_bound(self):
        store = self.store_with_room(8)
        store.append_jsonl('records', 123)
        store.append_jsonl('records', 456)
        with self.assertRaises(StorageBudgetExceeded) as exc:
            store.append_jsonl('records', 0)
        self.assertIsInstance(exc.exception, BudgetExceeded)
        self.assertEqual(exc.exception.kind, 'storage')
        self.assertEqual((self.root / 'records').read_bytes(), b'123\n456\n')

    def test_replace_peak_preserves_old(self):
        store = self.store_with_room(10)
        store.put_bytes('item', b'123456')
        with self.assertRaises(StorageBudgetExceeded):
            store.put_bytes('item', b'abcdef')
        self.assertEqual((self.root / 'item').read_bytes(), b'123456')

    def test_concurrent_instances(self):
        store = self.store_with_room(104)
        ctx = multiprocessing.get_context('fork')
        gate, results = ctx.Event(), ctx.Queue()
        processes = [ctx.Process(target=worker, args=(str(self.root), store.max_bytes, gate, results)) for _ in range(2)]
        for process in processes:
            process.start()
        gate.set()
        for process in processes:
            process.join(10)
            self.assertEqual(process.exitcode, 0)
        self.assertEqual(sorted(results.get(timeout=2) for _ in processes), [False, True])
        self.assertLessEqual(sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file()), store.max_bytes)

    def test_policy_immutable(self):
        store = self.store_with_room(100)
        for limit in (store.max_bytes + 1, store.max_bytes - 1):
            with self.assertRaises(ValueError):
                PrivateRunStorage(self.root, limit)
        self.assertEqual(PrivateRunStorage(self.root, store.max_bytes).describe(), store.describe())

    def test_symlinks_blocked(self):
        store = self.store_with_room(100)
        with tempfile.TemporaryDirectory() as outside:
            (self.root / 'escape').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                store.put_bytes('escape/file', b'x')
            self.assertFalse((Path(outside) / 'file').exists())

    def test_nan_no_mutation(self):
        store = self.store_with_room(100)
        store.save_json('file', {'a': 1})
        before = (self.root / 'file').read_bytes()
        for write in (lambda: store.save_json('file', float('nan')),
                      lambda: store.append_jsonl('file', float('nan'))):
            with self.assertRaises(ValueError):
                write()
            self.assertEqual((self.root / 'file').read_bytes(), before)

    def test_stream_append_and_exclusive(self):
        store = self.store_with_room(100)
        store.put_bytes('marker', b'', exclusive=True)
        with self.assertRaises(FileExistsError):
            store.put_bytes('marker', b'', exclusive=True)
        with (self.root / 'ledger').open('a+', encoding='utf-8') as stream:
            stream.seek(0)
            store.append_jsonl_stream(stream, {'é': 1})
            self.assertEqual(stream.tell(), len('{"é": 1}\n'.encode()))
        self.assertEqual((self.root / 'ledger').read_bytes(), '{"é": 1}\n'.encode())

    def test_nested_and_stream_limit(self):
        store = self.store_with_room(6)
        store.put_bytes('nested/file', b'x')
        with (self.root / 'ledger').open('a+', encoding='utf-8') as stream:
            store.append_jsonl_stream(stream, 123)
            position = stream.tell()
            with self.assertRaises(StorageBudgetExceeded):
                store.append_jsonl_stream(stream, 9)
            self.assertEqual(stream.tell(), position)
        self.assertEqual((self.root / 'ledger').read_bytes(), b'123\n')

    def test_policy_must_fit(self):
        with self.assertRaises(StorageBudgetExceeded):
            PrivateRunStorage(self.root, 0)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['.storage.lock'])


if __name__ == '__main__':
    unittest.main()
