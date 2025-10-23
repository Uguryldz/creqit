import creqit
from creqit.tests import IntegrationTestCase


class TestSequence(IntegrationTestCase):
	def generate_sequence_name(self) -> str:
		return self._testMethodName + "_" + creqit.generate_hash(length=5)

	def test_set_next_val(self):
		seq_name = self.generate_sequence_name()
		creqit.db.create_sequence(seq_name, check_not_exists=True, temporary=True)

		next_val = creqit.db.get_next_sequence_val(seq_name)
		creqit.db.set_next_sequence_val(seq_name, next_val + 1)
		self.assertEqual(next_val + 1, creqit.db.get_next_sequence_val(seq_name))

		next_val = creqit.db.get_next_sequence_val(seq_name)
		creqit.db.set_next_sequence_val(seq_name, next_val + 1, is_val_used=True)
		self.assertEqual(next_val + 2, creqit.db.get_next_sequence_val(seq_name))

	def test_create_sequence(self):
		seq_name = self.generate_sequence_name()
		creqit.db.create_sequence(seq_name, max_value=2, cycle=True, temporary=True)
		creqit.db.get_next_sequence_val(seq_name)
		creqit.db.get_next_sequence_val(seq_name)
		self.assertEqual(1, creqit.db.get_next_sequence_val(seq_name))

		seq_name = self.generate_sequence_name()
		creqit.db.create_sequence(seq_name, max_value=2, temporary=True)
		creqit.db.get_next_sequence_val(seq_name)
		creqit.db.get_next_sequence_val(seq_name)

		try:
			creqit.db.get_next_sequence_val(seq_name)
		except creqit.db.SequenceGeneratorLimitExceeded:
			pass
		else:
			self.fail("NEXTVAL didn't raise any error upon sequence's end")

		# without this, we're not able to move further
		# as postgres doesn't allow moving further in a transaction
		# when an error occurs
		creqit.db.rollback()

		seq_name = self.generate_sequence_name()
		creqit.db.create_sequence(seq_name, min_value=10, max_value=20, increment_by=5, temporary=True)
		self.assertEqual(10, creqit.db.get_next_sequence_val(seq_name))
		self.assertEqual(15, creqit.db.get_next_sequence_val(seq_name))
		self.assertEqual(20, creqit.db.get_next_sequence_val(seq_name))
